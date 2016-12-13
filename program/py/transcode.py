#!/usr/bin/env   python

import sys
import os
import subprocess
import string
import time
import datetime
import shutil
import stat
#import utils

if len(sys.argv) != 4:
    print ("input params error!")
    os._exit(1)

src_media_url=sys.argv[1]
trans_profile=sys.argv[2]
dst_format=sys.argv[3]

FFMPEG=""
mp4info=""
mp4fragment=""
python_2_7=""
mp4_dash_script=""
mp4_tool_path=""
py_path=""
work_path=""
dst_video_path=""
dst_hls_path=""
dst_dash_path=""



def prepare():
    global FFMPEG
    global mp4fragment
    global mp4_dash_script
    global python_2_7
    global mp4_tool_path

    global py_path
    global work_path
    global dst_video_path
    global dst_hls_path
    global dst_dash_path

    print ("===prepare===")

    py_path=os.path.dirname(os.path.realpath(__file__))
    str_t="py-->%s"%(py_path)
    print (str_t)

    work_path = os.path.dirname(py_path)
    str_t = "work_path-->%s"%(work_path)
    print (str_t)

    dst_video_path = os.path.join(work_path,'transcode_root')
    if os.path.exists(dst_video_path):
        shutil.rmtree(dst_video_path)
    os.makedirs(dst_video_path)

    dst_hls_path = os.path.join(dst_video_path,'hls')
    if os.path.exists(dst_hls_path):
        shutil.rmtree(dst_hls_path)
    os.makedirs(dst_hls_path)

    dst_dash_path = os.path.join(dst_video_path,'dash')
    if os.path.exists(dst_dash_path):
        shutil.rmtree(dst_dash_path)
    os.makedirs(dst_dash_path)

    FFMPEG= os.path.join(work_path,'ffmpeg')
    os.chmod(FFMPEG, stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)

    mp4_tool_path = os.path.join(work_path,'mp4tools')
    mp4fragment   = os.path.join(mp4_tool_path,'mp4fragment')
    mp4_dash_script = os.path.join(mp4_tool_path, 'mp4-dash.py')
    python_2_7 = os.path.join(mp4_tool_path, 'python2.7')

def trans_param_set(profile):
    trans_param = ''
    if profile == 'biaoqing':
        video_param = " -pix_fmt yuv420p -filter_complex 'yadif,fps=25, scale=640:-1:flags=fast_bilinear' -c:v libx264 -b:v 300K -preset slow "
        audio_param = " -c:a libfdk_aac -b:a 64k -ar 44100 -profile:a aac_he "
        format_param = " -f mp4 "
    elif profile == 'gaoqing':
        video_param = " -pix_fmt yuv420p -filter_complex 'yadif,fps=25, scale=960:-1:flags=fast_bilinear' -c:v libx264 -b:v 500K -preset slow "
        audio_param = " -c:a libfdk_aac -b:a 64k -ar 44100 -profile:a aac_he "
        format_param = " -f mp4 "

    trans_param = '{0} {1} {2} '.format(video_param, audio_param, format_param)
    return trans_param

def transcode(video_src,profile):
    global FFMPEG
    global dst_video_path

    trans_param = trans_param_set(profile)
    dst_mp4_video = "/dev/null"
    pass1_param = trans_param + "-pass 1"
    ff_trans_cmd ='{0} -y -i "{1}" {2} {3}'.format(FFMPEG, video_src, pass1_param, dst_mp4_video )
    print(ff_trans_cmd)
    subprocess.call(ff_trans_cmd, shell=True)

    pass2_param = trans_param + "-pass 2"
    dst_mp4_video = dst_video_path + "/dst_video.mp4"
    ff_trans_cmd ='{0} -y -i "{1}" {2} {3}'.format(FFMPEG, video_src, pass2_param, dst_mp4_video )
    print(ff_trans_cmd)
    subprocess.call(ff_trans_cmd, shell=True)

    return dst_mp4_video

def generate_hls(mp4_video):
    global FFMPEG
    global dst_hls_path

    hls_cmd =" -c copy -bsf:v h264_mp4toannexb -flags -global_header -map 0:0 -map 0:1 -f segment  -segment_list {0}/video.m3u8  -segment_time 10 {0}/out_video_%d.ts ".format(dst_hls_path)
    ff_hls_cmd  = '{0} -y -i "{1}" {2} '.format(FFMPEG, mp4_video, hls_cmd )
    print(ff_hls_cmd)
    subprocess.call(ff_hls_cmd, shell=True)

    return

def generate_raw_dash(mp4_video):
    global mp4_tool_path
    global mp4fragment
    global mp4_dash_script

    mp4fragment_tmp_mp4 = os.path.join(dst_video_path, 'output_fragment.mp4')
    mp4fragment_cmd = '{0} {1} {2}'.format(mp4fragment, mp4_video,mp4fragment_tmp_mp4)
    print ('mp4fragment_cmd is: {0}'.format(mp4fragment_cmd))
    subprocess.call(mp4fragment_cmd, shell=True)

    if os.path.exists(dst_dash_path):
        shutil.rmtree(dst_dash_path)

    mp4_to_dash_cmd = '{0} {1} --exec-dir={2} --use-segment-timeline ' \
                      ' -o {3} {4}'.format(python_2_7,mp4_dash_script,mp4_tool_path,dst_dash_path,mp4fragment_tmp_mp4)

    print ('mp4 to dash cmd is {0}'.format(mp4_to_dash_cmd))
    print mp4_to_dash_cmd

    subprocess.call(mp4_to_dash_cmd, shell=True)
    os.remove(mp4fragment_tmp_mp4)

    return

def transcode_package():
    global src_media_url
    global trans_profile
    global dst_format
    #mkdir,set global variable
    prepare()
    mp4_video = transcode(src_media_url,trans_profile)
    generate_hls(mp4_video)
    generate_raw_dash(mp4_video)

    return

if __name__ == "__main__":
    transcode_package()

