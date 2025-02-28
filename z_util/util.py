import os
import shutil

def Traversal(filedir):
    file_list=[]
    for root,dirs,files in os.walk(filedir):
        for file in files:
            file_list.append(os.path.join(root,file)) 
        for dir in dirs:
            Traversal(dir)
    return file_list

def is_img(path):
    ext = os.path.splitext(path)[1]
    ext = ext.lower()
    if ext in ['.jpg','.png','.jpeg','.bmp']:
        return True
    else:
        return False

def is_video(path):
    ext = os.path.splitext(path)[1]
    ext = ext.lower()
    if ext in ['.mp4','.flv','.avi','.mov','.mkv','.wmv','.rmvb','.mts','.m2ts']:
        return True
    else:
        return False

def is_imgs(paths):
    tmp = []
    for path in paths:
        if is_img(path):
            tmp.append(path)
    return tmp

def is_videos(paths):
    tmp = []
    for path in paths:
        if is_video(path):
            tmp.append(path)
    return tmp  

def is_dirs(paths):
    tmp = []
    for path in paths:
        if os.path.isdir(path):
            tmp.append(path)
    return tmp  

def  writelog(path,log,isprint=False):
    f = open(path,'a+')
    f.write(log+'\n')
    f.close()
    if isprint:
        print(log)

def makedirs(path):
    if os.path.isdir(path):
        print(path,'existed')
    else:
        os.makedirs(path)
        print('makedir:',path)

def clean_tempfiles(tmp_init=True):
    if os.path.isdir('./tmp'):   
        shutil.rmtree('./tmp')
    if tmp_init:
        os.makedirs('./tmp')
        os.makedirs('./tmp/video2image')
        os.makedirs('./tmp/addmosaic_image')
        os.makedirs('./tmp/mosaic_crop')
        os.makedirs('./tmp/replace_mosaic')
        os.makedirs('./tmp/mosaic_mask')
        os.makedirs('./tmp/ROI_mask')
        os.makedirs('./tmp/ROI_mask_check')
        os.makedirs('./tmp/style_transfer')

def file_init(opt):
    if not os.path.isdir(opt.result_dir):
        os.makedirs(opt.result_dir)
        print('makedir:',opt.result_dir)
    clean_tempfiles(True)

def second2stamp(s):
    h = int(s/3600)
    s = int(s%3600)
    m = int(s/60)
    s = int(s%60)

    return "%02d:%02d:%02d" % (h, m, s)

def get_bar(percent,num = 25):
    bar = '['
    for i in range(num):
        if i < round(percent/(100/num)):
            bar += '#'
        else:
            bar += '-'
    bar += ']'
    return bar+' '+str(round(percent,2))+'%'

def copyfile(src,dst):
    try:
        shutil.copyfile(src, dst)
    except Exception as e:
        print(e)

def opt2str(opt):
    message = ''
    message += '---------------------- Options --------------------\n'
    for k, v in sorted(vars(opt).items()):
        message += '{:>25}: {:<35}\n'.format(str(k), str(v))
    message += '----------------- End -------------------'
    return message
