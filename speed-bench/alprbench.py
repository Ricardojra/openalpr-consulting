import argparse
from multiprocessing import cpu_count
import os
import platform
import re
from threading import Thread, Lock
from time import time, sleep
import urllib
from alprstream import AlprStream
from openalpr import Alpr
from vehicleclassifier import VehicleClassifier


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
        self.quiet = quiet
        self.message('Initializing...')
        self.streams = streams
        if isinstance(resolution, str):
            if resolution == 'all':
                self.resolution = ['vga', '720p', '1080p', '4k']
            else:
                self.resolution = [resolution]
        elif isinstance(resolution, list):
            self.resolution = resolution
        else:
            raise ValueError('Expected list or str for resolution, but received {}'.format(resolution))
        self.downloads = downloads
        if not os.path.exists(self.downloads):
            os.mkdir(self.downloads)
        self.threads_active = False
        self.frame_counter = 0
        self.mutex = Lock()

        # Detect operating system
        if platform.system().lower().find('linux') == 0:
            operating = 'linux'
            self.message('\tOperating system: Linux')
        elif platform.system().lower().find('windows') == 0:
            operating = 'windows'
            self.message('\tOperating system: Windows')
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
        self.message('\tRuntime data: {}'.format(self.runtime))
        self.message('\tOpenALPR configuration: {}'.format(self.config))

    def __call__(self):
        """Run threaded benchmarks on all requested resolutions."""
        videos = self.download_benchmarks()
        alprstream = AlprStream(frame_queue_size=10)
        name_regex = re.compile('(?<=\/)[^\.\/]+')
        self.threads_active = True
        print('Benchmarking on {} threads...'.format(cpu_count()))

        for v in videos:
            self.frame_counter = 0
            threads = []
            alprstream.connect_video_file(v, 0)
            for i in range(cpu_count()):
                threads.append(Thread(target=self.worker, args=(alprstream, )))
                threads[i].setDaemon(True)
            start = time()
            for t in threads:
                t.start()
            while len(threads) > 0:
                try:
                    threads = [t.join() for t in threads if t is not None and t.isAlive()]
                except KeyboardInterrupt:
                    print('\n\nCtrl-C received! Sending kill to threads...')
                    self.threads_active = False
                    break
            elapsed = time() - start
            print('\t{} = {:.1f} fps ({} frames)'.format(
                name_regex.findall(v)[-1], self.frame_counter/elapsed, self.frame_counter))

    def download_benchmarks(self):
        """Save requested benchmark videos locally.

        :return [str] videos: Filepaths to downloaded videos.
        """
        videos = []
        endpoint = 'http://download.openalpr.com/bench'
        files = ['vga.webm', '720p.mp4', '1080p.mp4', '4k.mp4']
        existing = os.listdir(self.downloads)
        self.message('Downloading benchmark videos...')
        for f in files:
            short = f.split('.')[0]
            if short in self.resolution:
                out = os.path.join(self.downloads, f)
                videos.append(out)
                if f not in existing:
                    _ = urllib.urlretrieve(os.path.join(endpoint, f), out)
                    self.message('\tDownloaded {}'.format(short))
                else:
                    self.message('\tFound local {}'.format(short))
        return videos

    def message(self, msg):
        """Control verbosity of output.

        :param str msg: Message to display.
        :return: None
        """
        if not self.quiet:
            print(msg)

    def worker(self, alprstream):
        """Worker thread for a single stream and Alpr combination.

        :param alprstream: OpenALPR instance to manage the video stream.
        :return: None
        """
        alpr = Alpr('us', self.config, self.runtime)
        vehicle = VehicleClassifier(self.config, self.runtime)
        while alprstream.video_file_active() or alprstream.get_queue_size() > 0:
            if not self.threads_active:
                break
            if alprstream.get_queue_size() == 0:
                sleep(0.1)
                continue
            _ = alprstream.pop_completed_groups_and_recognize_vehicle(vehicle)
            _ = alprstream.process_frame(alpr)
            self.mutex.acquire()
            self.frame_counter += 1
            self.mutex.release()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Benchmark OpenALPR software speed at various video resolutions',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--download_dir', type=str, default='/tmp/alprbench', help='folder to save videos')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress all output besides final results')
    parser.add_argument('-r', '--resolution', type=str, default='all', help='video resolution to benchmark on')
    parser.add_argument('-s', '--streams', type=int, default=1, help='number of camera streams to simulate')
    parser.add_argument('--config', type=str, help='path to OpenALPR config, detects Windows/Linux and uses defaults')
    parser.add_argument('--runtime', type=str, help='path to runtime data, detects Windows/Linux and uses defaults')
    args = parser.parse_args()

    if ',' in args.resolution:
        args.resolution = [r.strip() for r in args.resolution.split(',')]
    bench = AlprBench(
        args.streams,
        args.resolution,
        args.download_dir,
        args.runtime,
        args.config,
        args.quiet)
    bench()
