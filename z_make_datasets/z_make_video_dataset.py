import os, sys

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

sys.path.append("..")
import datetime
import time
import numpy as np
import cv2
from z_models import runmodel, loadmodel
import z_util.image_processing as impro
from z_util import util, ffmpeg
from z_cores.options import Options

opt = Options()
opt.parser.add_argument('--datadir', type=str,
                        default='',
                        help='')
opt.parser.add_argument('--savedir', type=str, default='../datasets/demosaic', help='')
opt.parser.add_argument('--interval', type=int, default=30, help='interval of split video ')
opt.parser.add_argument('--time', type=int, default=30, help='split video time')
opt.parser.add_argument('--minmaskarea', type=int, default=2000, help='')
opt.parser.add_argument('--quality', type=int, default=45, help='minimal quality')
opt.parser.add_argument('--outsize', type=int, default=286, help='')
opt.parser.add_argument('--startcnt', type=int, default=0, help='')
opt.parser.add_argument('--minsize', type=int, default=96, help='minimal roi size')
opt = opt.getparse()
opt.model_path = '../z_models/add_youknow.pth'
opt.mask_threshold = 96

util.makedirs(opt.savedir)
util.writelog(os.path.join(opt.savedir, 'opt.txt'),
              str(time.asctime(time.localtime(time.time()))) + '\n' + util.opt2str(opt))

videopaths = util.Traversal(opt.datadir)
if len(videopaths) == 0:
    videopaths = opt.datadir.split(",")
    videopaths = sorted(videopaths)

videopaths = util.is_videos(videopaths)
# random.shuffle(videopaths)

# def network
net = loadmodel.bisenet(opt, 'roi')

video_cnt = 1
starttime = datetime.datetime.now()
for videopath in videopaths:
    # generate datasets
    print('Generate datasets...')
    origindir = os.path.join(opt.savedir, 'train_B')
    maskdir = os.path.join(opt.savedir, 'train_A')
    util.makedirs(origindir)
    util.makedirs(maskdir)

    util.clean_tempfiles()
    ffmpeg.video2image(videopath, './tmp/video2image/%05d.' + opt.tempimage_type, opt.fps)

    endtime = datetime.datetime.now()
    print(str(video_cnt) + '/' + str(len(videopaths)) + ' ',
          util.get_bar(100 * video_cnt / len(videopaths), 35), '',
          util.second2stamp((endtime - starttime).seconds) + '/' + util.second2stamp(
              (endtime - starttime).seconds / video_cnt * len(videopaths)))

    imagepaths = util.Traversal('./tmp/video2image')
    imagepaths = sorted(imagepaths)
    imgs = []
    masks = []
    mask_flag = False

    for imagepath in imagepaths:
        img = impro.imread(imagepath)
        mask = runmodel.get_ROI_position(img, net, opt, keepsize=True)[0]
        imgs.append(img)
        masks.append(mask)
        if not mask_flag:
            mask_avg = mask.astype(np.float64)
            mask_flag = True
        else:
            mask_avg += mask.astype(np.float64)

    mask_avg = np.clip(mask_avg / len(imagepaths), 0, 255).astype('uint8')
    mask_avg = impro.mask_threshold(mask_avg, 20, 64)
    if not opt.all_mosaic_area:
        mask_avg = impro.find_mostlikely_ROI(mask_avg)
    # x, y, size, area = impro.boundingSquare(mask_avg, Ex_mul=random.uniform(1.1, 1.5))

    cnt = 0
    for i in range(len(imagepaths)):
        x, y, size, area = impro.boundingSquare(masks[i], Ex_mul=1.5)
        if area > opt.minmaskarea and size > opt.minsize * 1.5 and impro.Q_lapulase(imgs[i]) > opt.quality:
            img = impro.resize(imgs[i][y - size:y + size, x - size:x + size], opt.outsize, interpolation=cv2.INTER_CUBIC)
            mask = impro.resize(masks[i][y - size:y + size, x - size:x + size], opt.outsize, interpolation=cv2.INTER_CUBIC)
            impro.imwrite(os.path.join(origindir, str(video_cnt) + '_' + '%05d' % (i + 1) + '.jpg'), img)
            impro.imwrite(os.path.join(maskdir, str(video_cnt) + '_' + '%05d' % (i + 1) + '.png'), mask)
        else:
            print(imagepaths[i])
            cnt += 1
    print("bad pic:", cnt)

video_cnt += 1


