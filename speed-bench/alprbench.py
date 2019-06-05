import argparse
from multiprocessing import cpu_count
import os
import platform
import urllib
from openalpr import Alpr
from alprstream import AlprStream


class AlprBench:
    """Benchmark OpenALPR software speed for various video resolutions.

    :param int streams: Number of camera streams to simulate.
    :param str or [str] resolution: Resolution(s) of videos to benchmark.
    :param str downloads: Folder to save benchmark videos to.
    :param str runtime: Path to runtime data folder.
    :param str config: Path to OpenALPR configuration file.
    :param bool quiet: Suppress all output besides final results.
    """

    def __init__(self, streams, resolution, downloads='/tmp/alprbench', runtime=None, config=None, quiet=False):

        # Transfer parameters to attributes
        self.streams = streams
        self.quiet = quiet
        if resolution == 'all':
            self.resolution = ['vga', '720p', '1080p', '4k']
        elif isinstance(resolution, str):
            self.resolution = [resolution]
        self.downloads = downloads
        if not os.path.exists(self.downloads):
            os.mkdir(self.downloads)

        # Detect operating system
        if platform.system().lower().find('linux') == 0:
            operating = 'linux'
        elif platform.system().lower().find('windows') == 0:
            operating = 'windows'
        else:
            raise OSError('Detected OS other than Linux or Windows')

        # Define default runtime and config paths if not specified
        if runtime is None:
            self.runtime = '/usr/share/openalpr/runtime_data'
            if operating == 'windows':
                self.runtime = 'C:/OpenALPR/Agent' + self.runtime
        if config is None:
            self.config = '/usr/share/openalpr/config/openalpr.defaults.conf'
            if operating == 'windows':
                self.config = 'C:/OpenALPR/Agent' + self.config
        self.message('Runtime data: {}'.format(self.runtime))
        self.message('OpenALPR configuration: {}'.format(self.config))

    def __call__(self):
        videos = self.download_benchmarks()
        alprs, alprstreams = self.init_alpr()

    def download_benchmarks(self):
        """Save requested benchmark videos locally.

        :return [str] videos: Filepaths to downloaded videos.
        """
        videos = []
        endpoint = 'http://download.openalpr.com/bench'
        files = ['vga.webm', '720p.mp4', '1080p.mp4', '4k.mp4']
        existing = os.listdir(self.downloads)
        for f in files:
            short = f.split('.')[0]
            if short in self.resolution:
                out = os.path.join(self.downloads, f)
                videos.append(out)
                if f not in existing:
                    _ = urllib.request.urlretrieve(os.path.join(endpoint, f), out)
                    self.message('Downloaded {}'.format(short))
                else:
                    self.message('{} already exists'.format(short))
        return videos

    def init_alpr(self):
        """Load Alpr and AlprStream objects into memory."""
        alprs = []
        alprstreams = []
        cores = cpu_count()
        alpr = Alpr('us', '', '')

    def message(self, msg):
        """Control verbosity of output."""
        if not self.quiet:
            print(msg)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Benchmark OpenALPR software speed at various video resolutions',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--download_dir', type=str, default='/tmp/alprbench', help='folder to save videos')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress all output besides final results')
    parser.add_argument('-r', '--resolution', type=str, default='all', choices=['vga', '720p', '1080p', '4k'],
                        help='video resolution to benchmark on')
    parser.add_argument('-s', '--streams', type=int, default=1, help='number of camera streams to simulate')
    parser.add_argument('--config', type=str, help='path to OpenALPR config, detects Windows/Linux and uses defaults')
    parser.add_argument('--runtime', type=str, help='path to runtime data, detects Windows/Linux and uses defaults')
    args = parser.parse_args()

    bench = AlprBench(args.streams, args.resolution, args.download_dir, args.runtime, args.config, args.quiet)
    bench()
