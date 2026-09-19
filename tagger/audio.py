import re
import base64
from pathlib import Path
from typing import Optional, Any
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TCON, TDRC, TRCK, TPOS, APIC, USLT, ID3NoHeaderError
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus

from tagger.models import TrackMetadata, AudioFileInfo

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".m4a", ".mp4", ".alac", ".ogg", ".opus", ".wav", ".aiff"}

class AudioTagEngine:
    def __init__(self):
        pass

    def read_file_info(self, file_path: Path) -> AudioFileInfo:
        ext = file_path.suffix.lower()
        info = AudioFileInfo(
            path=file_path,
            filename=file_path.name,
            extension=ext,
            folder=file_path.parent
        )

        try:
            audio = mutagen.File(file_path)
            if audio is not None and audio.tags is not None:
                tags = audio.tags

                # MP3 ID3
                if isinstance(tags, ID3) or hasattr(tags, "getall"):
                    info.existing_title = self._get_id3_text(tags, "TIT2")
                    info.existing_artist = self._get_id3_text(tags, "TPE1")
                    info.existing_album_artist = self._get_id3_text(tags, "TPE2")
                    info.existing_album = self._get_id3_text(tags, "TALB")
                    info.existing_genre = self._get_id3_text(tags, "TCON")
                    info.existing_year = self._get_id3_text(tags, "TDRC") or self._get_id3_text(tags, "TYER")
                    tpos = self._get_id3_text(tags, "TPOS")
                    if tpos:
                        try:
                            info.existing_disc_num = int(tpos.split("/")[0])
                        except ValueError:
                            pass
                    trck = self._get_id3_text(tags, "TRCK")
                    if trck:
                        m_dt = re.match(r'^0*(\d+)[-.]0*(\d+)', trck.split("/")[0])
                        if m_dt:
                            if info.existing_disc_num is None:
                                info.existing_disc_num = int(m_dt.group(1))
                            info.existing_track_num = int(m_dt.group(2))
                        else:
                            try:
                                info.existing_track_num = int(trck.split("/")[0])
                            except ValueError:
                                pass

                # FLAC / OGG / Vorbis
                elif isinstance(audio, (FLAC, OggVorbis, OggOpus)) or hasattr(tags, "items"):
                    info.existing_title = self._get_vorbis_text(tags, "TITLE")
                    info.existing_artist = self._get_vorbis_text(tags, "ARTIST")
                    info.existing_album_artist = self._get_vorbis_text(tags, "ALBUMARTIST") or self._get_vorbis_text(tags, "ALBUM ARTIST")
                    info.existing_album = self._get_vorbis_text(tags, "ALBUM")
                    info.existing_genre = self._get_vorbis_text(tags, "GENRE")
                    info.existing_year = self._get_vorbis_text(tags, "DATE") or self._get_vorbis_text(tags, "YEAR")
                    disc = self._get_vorbis_text(tags, "DISCNUMBER")
                    if disc:
                        try:
                            info.existing_disc_num = int(disc.split("/")[0])
                        except ValueError:
                            pass
                    trck = self._get_vorbis_text(tags, "TRACKNUMBER")
                    if trck:
                        m_dt = re.match(r'^0*(\d+)[-.]0*(\d+)', trck.split("/")[0])
                        if m_dt:
                            if info.existing_disc_num is None:
                                info.existing_disc_num = int(m_dt.group(1))
                            info.existing_track_num = int(m_dt.group(2))
                        else:
                            try:
                                info.existing_track_num = int(trck.split("/")[0])
                            except ValueError:
                                pass

                # M4A / MP4
                elif isinstance(audio, MP4):
                    info.existing_title = self._get_mp4_text(tags, "\xa9nam")
                    info.existing_artist = self._get_mp4_text(tags, "\xa9ART")
                    info.existing_album_artist = self._get_mp4_text(tags, "aART")
                    info.existing_album = self._get_mp4_text(tags, "\xa9alb")
                    info.existing_genre = self._get_mp4_text(tags, "\xa9gen")
                    info.existing_year = self._get_mp4_text(tags, "\xa9day")
                    disk = tags.get("disk")
                    if disk and isinstance(disk[0], tuple):
                        info.existing_disc_num = disk[0][0]
                    trkn = tags.get("trkn")
                    if trkn and isinstance(trkn[0], tuple):
                        info.existing_track_num = trkn[0][0]

        except Exception as e:
            # Corrupted or unreadable tags
            pass

        # Fallback disc / track number detection from folder name or filename
        if info.existing_disc_num is None:
            m_folder = re.search(r'(?:CD|Disc|Disk)\s*(\d+)', file_path.parent.name, re.I)
            if m_folder:
                info.existing_disc_num = int(m_folder.group(1))

        if info.existing_disc_num is None or info.existing_track_num is None:
            m_fn = re.match(r'^0*(\d+)[-.]0*(\d+)', file_path.name)
            if m_fn:
                if info.existing_disc_num is None:
                    info.existing_disc_num = int(m_fn.group(1))
                if info.existing_track_num is None:
                    info.existing_track_num = int(m_fn.group(2))

        return info

    def _get_id3_text(self, tags: Any, frame_id: str) -> Optional[str]:
        frames = tags.getall(frame_id)
        if frames and hasattr(frames[0], "text") and frames[0].text:
            return str(frames[0].text[0]).strip()
        return None

    def _get_vorbis_text(self, tags: Any, key: str) -> Optional[str]:
        vals = tags.get(key) or tags.get(key.lower())
        if vals:
            return str(vals[0]).strip()
        return None

    def _get_mp4_text(self, tags: Any, key: str) -> Optional[str]:
        vals = tags.get(key)
        if vals and isinstance(vals, list) and len(vals) > 0:
            return str(vals[0]).strip()
        return None

    def apply_tags(
        self,
        file_path: Path,
        meta: TrackMetadata,
        cover_image_bytes: Optional[bytes] = None,
        lyrics_text: Optional[str] = None,
        clean_junk_tags: bool = True,
        enabled_tags: Optional[dict] = None,
        multi_disc_format: bool = True
    ) -> bool:
        """
        Writes TrackMetadata, optional cover art, and optional lyrics to the audio file.
        Cleans junk promo/comment tags if clean_junk_tags is True.
        Only writes tags enabled in enabled_tags (or all if enabled_tags is None).
        """
        ext = file_path.suffix.lower()
        try:
            if ext == ".mp3":
                return self._apply_mp3_tags(file_path, meta, cover_image_bytes, lyrics_text, clean_junk_tags, enabled_tags, multi_disc_format)
            elif ext == ".flac":
                return self._apply_flac_tags(file_path, meta, cover_image_bytes, lyrics_text, clean_junk_tags, enabled_tags, multi_disc_format)
            elif ext in [".m4a", ".mp4", ".alac"]:
                return self._apply_mp4_tags(file_path, meta, cover_image_bytes, lyrics_text, clean_junk_tags, enabled_tags, multi_disc_format)
            elif ext in [".ogg", ".opus"]:
                return self._apply_ogg_tags(file_path, meta, cover_image_bytes, lyrics_text, clean_junk_tags, enabled_tags, multi_disc_format)
            else:
                # Fallback generic mutagen save
                en = enabled_tags or {}
                def is_on(k: str) -> bool: return en.get(k, True)
                audio = mutagen.File(file_path, easy=True)
                if audio is not None:
                    if is_on("title") and meta.title: audio["title"] = meta.title
                    if is_on("artist") and meta.artist: audio["artist"] = meta.artist
                    if is_on("album_artist") and meta.album_artist: audio["albumartist"] = meta.album_artist
                    if is_on("album") and meta.album: audio["album"] = meta.album
                    if is_on("genre") and meta.genre is not None: audio["genre"] = meta.genre
                    if is_on("year") and meta.year: audio["date"] = meta.year
                    if is_on("track_number") and meta.track_number:
                        audio["tracknumber"] = f"{meta.track_number:02d}"
                        if meta.disc_number:
                            audio["discnumber"] = f"{meta.disc_number:02d}"
                    audio.save()
                    return True
        except Exception as e:
            print(f"Error applying tags to {file_path}: {e}")
            return False
        return False

    def _apply_mp3_tags(
        self,
        file_path: Path,
        meta: TrackMetadata,
        cover_bytes: Optional[bytes],
        lyrics_text: Optional[str],
        clean_junk_tags: bool,
        enabled_tags: Optional[dict] = None,
        multi_disc_format: bool = True
    ) -> bool:
        en = enabled_tags or {}
        def is_on(k: str) -> bool: return en.get(k, True)

        try:
            id3 = ID3(file_path)
        except ID3NoHeaderError:
            id3 = ID3()

        if clean_junk_tags:
            junk_prefixes = ["COMM", "WXXX", "WCOM", "WOAR", "WOAF", "WOAS", "WORS", "WPAY", "TENC", "TSSE", "PRIV", "USER"]
            for key in list(id3.keys()):
                for junk in junk_prefixes:
                    if key.startswith(junk):
                        try:
                            del id3[key]
                        except Exception:
                            pass
                        break

        if is_on("title") and meta.title:
            id3.add(TIT2(encoding=3, text=[meta.title]))
        if is_on("artist") and meta.artist:
            id3.add(TPE1(encoding=3, text=[meta.artist]))
        if is_on("album_artist") and meta.album_artist:
            id3.add(TPE2(encoding=3, text=[meta.album_artist]))
        if is_on("album") and meta.album:
            id3.add(TALB(encoding=3, text=[meta.album]))
        if is_on("genre") and meta.genre is not None:
            id3.add(TCON(encoding=3, text=[meta.genre]))
        if is_on("year") and meta.year:
            id3.add(TDRC(encoding=3, text=[str(meta.year)]))

        if is_on("track_number") and meta.track_number:
            id3.add(TRCK(encoding=3, text=[f"{meta.track_number:02d}"]))

        if is_on("track_number") and meta.disc_number:
            tpos_val = f"{meta.disc_number:02d}"
            if meta.total_discs and meta.total_discs > 1:
                tpos_val += f"/{meta.total_discs:02d}"
            id3.add(TPOS(encoding=3, text=[tpos_val]))

        if is_on("lyrics") and lyrics_text:
            id3.delall("USLT")
            id3.add(USLT(encoding=3, lang="eng", desc="", text=lyrics_text))

        if is_on("cover") and cover_bytes:
            id3.delall("APIC")
            id3.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,  # Front cover
                desc="Cover",
                data=cover_bytes
            ))

        id3.save(file_path, v2_version=3)
        return True

    def _apply_flac_tags(
        self,
        file_path: Path,
        meta: TrackMetadata,
        cover_bytes: Optional[bytes],
        lyrics_text: Optional[str],
        clean_junk_tags: bool,
        enabled_tags: Optional[dict] = None,
        multi_disc_format: bool = True
    ) -> bool:
        audio = FLAC(file_path)
        en = enabled_tags or {}
        def is_on(k: str) -> bool: return en.get(k, True)

        if clean_junk_tags:
            junk_vorbis = ["COMMENT", "DESCRIPTION", "ENCODEDBY", "ENCODER", "URL", "CONTACT", "VENDOR"]
            for j in junk_vorbis:
                if j in audio:
                    del audio[j]
                if j.lower() in audio:
                    del audio[j.lower()]

        if is_on("title") and meta.title:
            audio["title"] = meta.title
        if is_on("artist") and meta.artist:
            audio["artist"] = meta.artist
        if is_on("album_artist") and meta.album_artist:
            audio["albumartist"] = meta.album_artist
        if is_on("album") and meta.album:
            audio["album"] = meta.album
        if is_on("genre") and meta.genre is not None:
            audio["genre"] = meta.genre
        if is_on("year") and meta.year:
            audio["date"] = str(meta.year)
        if is_on("track_number") and meta.track_number:
            audio["tracknumber"] = f"{meta.track_number:02d}"
            if meta.disc_number:
                audio["discnumber"] = f"{meta.disc_number:02d}"
            if meta.total_discs and meta.total_discs > 1:
                audio["disctotal"] = f"{meta.total_discs:02d}"

        if is_on("lyrics") and lyrics_text:
            audio["LYRICS"] = [lyrics_text]

        if is_on("cover") and cover_bytes:
            pic = Picture()
            pic.type = 3  # Front cover
            pic.mime = "image/jpeg"
            pic.desc = "Cover"
            pic.data = cover_bytes
            audio.clear_pictures()
            audio.add_picture(pic)

        audio.save()
        return True

    def _apply_mp4_tags(
        self,
        file_path: Path,
        meta: TrackMetadata,
        cover_bytes: Optional[bytes],
        lyrics_text: Optional[str],
        clean_junk_tags: bool,
        enabled_tags: Optional[dict] = None,
        multi_disc_format: bool = True
    ) -> bool:
        audio = MP4(file_path)
        en = enabled_tags or {}
        def is_on(k: str) -> bool: return en.get(k, True)

        if clean_junk_tags:
            junk_mp4 = ["\xa9cmt", "\xa9enc", "\xa9too"]
            for j in junk_mp4:
                if j in audio:
                    del audio[j]

        if is_on("title") and meta.title:
            audio["\xa9nam"] = [meta.title]
        if is_on("artist") and meta.artist:
            audio["\xa9ART"] = [meta.artist]
        if is_on("album_artist") and meta.album_artist:
            audio["aART"] = [meta.album_artist]
        if is_on("album") and meta.album:
            audio["\xa9alb"] = [meta.album]
        if is_on("genre") and meta.genre is not None:
            audio["\xa9gen"] = [meta.genre]
        if is_on("year") and meta.year:
            audio["\xa9day"] = [str(meta.year)]

        if is_on("track_number"):
            t_num = meta.track_number or 0
            t_total = meta.total_tracks or 0
            audio["trkn"] = [(t_num, t_total)]

            d_num = meta.disc_number or 1
            d_total = meta.total_discs or 1
            audio["disk"] = [(d_num, d_total)]

        if is_on("lyrics") and lyrics_text:
            audio["\xa9lyr"] = [lyrics_text]

        if is_on("cover") and cover_bytes:
            audio["covr"] = [MP4Cover(cover_bytes, imageformat=MP4Cover.FORMAT_JPEG)]

        audio.save()
        return True

    def _apply_ogg_tags(
        self,
        file_path: Path,
        meta: TrackMetadata,
        cover_bytes: Optional[bytes],
        lyrics_text: Optional[str],
        clean_junk_tags: bool,
        enabled_tags: Optional[dict] = None,
        multi_disc_format: bool = True
    ) -> bool:
        ext = file_path.suffix.lower()
        if ext == ".opus":
            audio = OggOpus(file_path)
        else:
            audio = OggVorbis(file_path)

        en = enabled_tags or {}
        def is_on(k: str) -> bool: return en.get(k, True)

        if clean_junk_tags:
            junk_ogg = ["COMMENT", "DESCRIPTION", "ENCODEDBY", "ENCODER", "URL"]
            for j in junk_ogg:
                if j in audio:
                    del audio[j]

        if is_on("title") and meta.title:
            audio["TITLE"] = [meta.title]
        if is_on("artist") and meta.artist:
            audio["ARTIST"] = [meta.artist]
        if is_on("album_artist") and meta.album_artist:
            audio["ALBUMARTIST"] = [meta.album_artist]
        if is_on("album") and meta.album:
            audio["ALBUM"] = [meta.album]
        if is_on("genre") and meta.genre is not None:
            audio["GENRE"] = [meta.genre]
        if is_on("year") and meta.year:
            audio["DATE"] = [str(meta.year)]
        if is_on("track_number") and meta.track_number:
            audio["TRACKNUMBER"] = [f"{meta.track_number:02d}"]
            if meta.disc_number:
                audio["DISCNUMBER"] = [f"{meta.disc_number:02d}"]
            if meta.total_discs and meta.total_discs > 1:
                audio["DISCTOTAL"] = [f"{meta.total_discs:02d}"]

        if is_on("lyrics") and lyrics_text:
            audio["LYRICS"] = [lyrics_text]

        if is_on("cover") and cover_bytes:
            pic = Picture()
            pic.type = 3
            pic.mime = "image/jpeg"
            pic.desc = "Cover"
            pic.data = cover_bytes
            encoded_pic = base64.b64encode(pic.write()).decode("ascii")
            audio["METADATA_BLOCK_PICTURE"] = [encoded_pic]

        audio.save()
        return True
