#!/usr/bin/env python3
import sys
import io
import zipfile

def repack_docx(mode):
    raw_data = sys.stdin.buffer.read()
    if not raw_data:
        return

    # clean -> сохраняем без сжатия (ZIP_STORED) для дельта-компрессии Git
    # smudge -> возвращаем стандартное сжатие (ZIP_DEFLATED) на диск
    compression = zipfile.ZIP_STORED if mode == "clean" else zipfile.ZIP_DEFLATED
    in_buf = io.BytesIO(raw_data)

    # Если файл не является валидным ZIP-архивом, передаем его без изменений
    if not zipfile.is_zipfile(in_buf):
        sys.stdout.buffer.write(raw_data)
        return

    in_buf.seek(0)
    out_buf = io.BytesIO()

    with zipfile.ZipFile(in_buf, "r") as zin, zipfile.ZipFile(out_buf, "w", compression=compression) as zout:
        # Сортируем файлы по имени и фиксируем дату для стабильности хэшей
        for item in sorted(zin.infolist(), key=lambda x: x.filename):
            content = zin.read(item.filename)
            new_info = zipfile.ZipInfo(filename=item.filename)
            new_info.date_time = (1980, 1, 1, 0, 0, 0)
            new_info.compress_type = compression
            zout.writestr(new_info, content)

    sys.stdout.buffer.write(out_buf.getvalue())

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "clean"
    repack_docx(action)