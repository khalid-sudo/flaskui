import zstandard as zstd
from io import BytesIO

def decompress_zst_file(file_path):
    try:
        with open(file_path, 'rb') as compressed_file:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(compressed_file) as reader:
                decompressed = BytesIO(reader.read())
                decompressed.seek(0)
                return decompressed
    except zstd.ZstdError:
        return None
