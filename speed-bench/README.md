# alprbench

Drive OpenALPR on all CPU cores to benchmark speed for various video resolutions

## Prequisites

* OpenALPR commercial or evaluation license
* Ubuntu 18.04, Ubuntu 16.04, or Windows 10
* Python3

## Installation

1. Download the OpenALPR [SDK](http://doc.openalpr.com/sdk.html#installation) 
2. Clone this repository

## Usage

View all command line options by running `python alprbench.py -h`

## Sample Output

```commandline
Initializing...
	Operating system: Linux
	CPU model: Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz	
	Runtime data: /usr/share/openalpr/runtime_data
	OpenALPR configuration: /usr/share/openalpr/config/openalpr.defaults.conf
Downloading benchmark videos...
	Found local vga
	Downloaded 720p
	Found local 1080p
	Found local 4k
Benchmarking on 12 threads...
	vga = 79.8 fps (10978 frames)
	720p = 59.8 fps (1126 frames)
	1080p = 39.5 fps (601 frames)
	4k = 32.0 fps (892 frames)
```