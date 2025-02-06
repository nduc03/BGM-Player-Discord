import hashlib
import posixpath
import aiohttp
import io
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode

def normalize_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = posixpath.normpath(parsed.path)
    query = urlencode(sorted(parse_qsl(parsed.query)))
    if parsed.path.endswith('/') and not path.endswith('/'):
        path += '/'
    return parsed._replace(netloc=netloc, path=path, query=query, fragment='').geturl()

async def download_file(url, destination):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(destination, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024**2*8):
                        f.write(chunk)
                print(f"Downloaded to {destination}")
            else:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Failed to download {url}",
                    headers=response.headers
                )


async def get(url) -> io.BufferedReader:
    cache_dir = Path('url_cache_dir')
    cache_dir.mkdir(exist_ok=True)

    normalized_url = normalize_url(url)

    filename = hashlib.md5(normalized_url.encode()).hexdigest()
    filepath = cache_dir / filename
    if not filepath.exists():
        await download_file(url, filepath)
    else:
        print(f"Using cached file: {filepath}")

    return filepath.open('rb')
