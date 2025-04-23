# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
from backup_media.cli import get_exif_date_taken, get_file_year, backup_media_files

class TestCLI(unittest.TestCase):

    @patch("backup_media.cli.Image.open")
    def test_get_exif_date_taken_valid(self, mock_image_open):
        # Mock EXIF data with a valid DateTimeOriginal
        mock_image = MagicMock()
        mock_image.getexif.return_value = {36867: "2023:01:01 12:00:00"}
        mock_image_open.return_value = mock_image

        result = get_exif_date_taken("test.jpg")
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    @patch("backup_media.cli.Image.open")
    def test_get_exif_date_taken_no_exif(self, mock_image_open):
        # Mock EXIF data with no DateTimeOriginal
        mock_image = MagicMock()
        mock_image.getexif.return_value = {}
        mock_image_open.return_value = mock_image

        result = get_exif_date_taken("test.jpg")
        self.assertIsNone(result)

    @patch("backup_media.cli.Image.open")
    def test_get_exif_date_taken_invalid_format(self, mock_image_open):
        # Mock invalid EXIF data
        mock_image = MagicMock()
        mock_image.getexif.return_value = {36867: "invalid_date"}
        mock_image_open.return_value = mock_image

        result = get_exif_date_taken("test.jpg")
        self.assertIsNone(result)

    @patch("backup_media.cli.Path.stat")
    def test_get_file_year_from_metadata(self, mock_stat):
        # Mock file modification time
        mock_stat.return_value.st_mtime = 1672531200  # 2023-01-01 00:00:00
        path = Path("test.jpg")

        with patch("backup_media.cli.get_exif_date_taken", return_value=None):
            result = get_file_year(path)
            self.assertEqual(result, 2023)

    @patch("backup_media.cli.Path.stat")
    def test_get_file_year_current_year_on_error(self, mock_stat):
        # Simulate an error in getting file metadata
        mock_stat.side_effect = Exception("Error")
        path = Path("test.jpg")

        with patch("backup_media.cli.get_exif_date_taken", return_value=None):
            result = get_file_year(path)
            self.assertEqual(result, datetime.now().year)

    def test_get_file_year_exif_date(self):
        # Mock file with EXIF date
        mock_path = MagicMock()
        mock_path.suffix = ".jpg"
        mock_path.is_file.return_value = True
        mock_path.stat.return_value.st_mtime = 1672531200

        with patch("backup_media.cli.get_exif_date_taken", return_value=datetime(2023, 1, 1)):
            result = get_file_year(mock_path)
            self.assertEqual(result, 2023)

    @patch("backup_media.cli.Path.exists")
    @patch("backup_media.cli.shutil.copy2")
    @patch("backup_media.cli.Path.mkdir")
    @patch("backup_media.cli.Path.rglob")
    def test_backup_media_files_copy(self, mock_rglob, mock_mkdir, mock_copy2, mock_exists):
        # Mock files in the SD card path
        mock_file = MagicMock()
        mock_file.suffix = ".jpg"
        mock_file.is_file.return_value = True
        mock_file.name = "test.jpg"
        mock_rglob.return_value = [mock_file]
        mock_exists.side_effect = [True, False]

        with patch("backup_media.cli.get_file_year", return_value=2023):
            backup_media_files("/sd_card", "/backup", dry_run=False, move_files=False)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_copy2.assert_called_once()


    @patch("backup_media.cli.Path.exists")
    @patch("backup_media.cli.shutil.move")
    @patch("backup_media.cli.Path.mkdir")
    @patch("backup_media.cli.Path.rglob")
    def test_backup_media_files_move(self, mock_rglob, mock_mkdir, mock_move, mock_exists):
        # Mock files in the SD card path
        mock_file = MagicMock()
        mock_file.suffix = ".jpg"
        mock_file.is_file.return_value = True
        mock_file.name = "test.jpg"
        mock_rglob.return_value = [mock_file]
        mock_exists.side_effect = [True, False]

        with patch("backup_media.cli.get_file_year", return_value=2023):
            backup_media_files("/sd_card", "/backup", dry_run=False, move_files=True)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_move.assert_called_once()

    @patch("backup_media.cli.Path.exists")
    @patch("backup_media.cli.shutil.copy2")
    @patch("backup_media.cli.Path.mkdir")
    @patch("backup_media.cli.Path.rglob")
    def test_backup_media_files_copy_dry_run(self, mock_rglob, mock_mkdir, mock_copy2, mock_exists):
        # Mock files in the SD card path
        mock_file = MagicMock()
        mock_file.suffix = ".jpg"
        mock_file.is_file.return_value = True
        mock_file.name = "test.jpg"
        mock_rglob.return_value = [mock_file]
        mock_exists.side_effect = [True, False]

        with patch("backup_media.cli.get_file_year", return_value=2023):
            with patch("builtins.print") as mock_print:
                backup_media_files("/sd_card", "/backup", dry_run=True, move_files=False)

        mock_mkdir.assert_not_called()
        mock_copy2.assert_not_called()
        mock_print.assert_called()

    @patch("backup_media.cli.Path.exists")
    @patch("backup_media.cli.shutil.move")
    @patch("backup_media.cli.Path.mkdir")
    @patch("backup_media.cli.Path.rglob")
    def test_backup_media_files_move_dry_run(self, mock_rglob, mock_mkdir, mock_move, mock_exists):
        # Mock files in the SD card path
        mock_file = MagicMock()
        mock_file.suffix = ".jpg"
        mock_file.is_file.return_value = True
        mock_file.name = "test.jpg"
        mock_rglob.return_value = [mock_file]
        mock_exists.side_effect = [True, False]

        mock_rglob.return_value = [mock_file]

        with patch("backup_media.cli.get_file_year", return_value=2023):
            with patch("builtins.print") as mock_print:
                backup_media_files("/sd_card", "/backup", dry_run=True, move_files=True)


        mock_mkdir.assert_not_called()
        mock_move.assert_not_called()
        mock_print.assert_called()


    def test_backup_media_files_invalid_sd_card_path(self):
        # Test with an invalid SD card path
        with patch("builtins.print") as mock_print:
            backup_media_files("/invalid_path", "/backup", dry_run=False, move_files=False)
            mock_print.assert_called_with("SD card path '/invalid_path' does not exist.")

    @patch("backup_media.cli.Path.exists")
    @patch("backup_media.cli.Path.glob")
    def test_backup_media_files_invalid_file(self, mock_glob, mock_exists):
        # Test with an invalid file
        mock_file = MagicMock()
        mock_file.is_file.return_value = False
        mock_glob.return_value = [mock_file]
        mock_exists.return_value = True

        with patch("logging.error") as mock_logerror:
            backup_media_files("/sd_card", "/backup", dry_run=False, move_files=False)
            mock_logerror.assert_called_with("Provided file is not a file.")

    @patch("backup_media.cli.Path.exists")
    @patch("backup_media.cli.Path.glob")
    def test_backup_media_files_invalid_extension(self, mock_glob, mock_exists):
        # Test with an invalid file extension
        mock_file = MagicMock()
        mock_file.suffix = ".txt"
        mock_file.is_file.return_value = True
        mock_glob.return_value = [mock_file]
        mock_exists.return_value = True

        with patch("logging.error") as mock_logerror:
            with patch("backup_media.cli.Path.rglob", return_value=[mock_file]):
                backup_media_files("/sd_card", "/backup", dry_run=False, move_files=False)
                mock_logerror.assert_called_with("file extension '%s' not in IMAGE_EXTENSIONS nor in VIDEO_EXTENSIONS", ".txt")
