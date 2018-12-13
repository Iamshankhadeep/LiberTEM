import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
from functools import partial
import asyncio
import time
import sys
import multiprocessing

import numpy as np
import psutil
import dask.distributed as dd

from libertem import api
from libertem.io.dataset import load
from libertem.executor.dask import AsyncDaskJobExecutor, DaskJobExecutor
from libertem.job.sum import SumFramesJob
from libertem.job.masks import ApplyMasksJob


# Since the interpreter is embedded, we have to set the Python executable.
# Otherwise we'd spawn new instances of Digital Micrograph instead of workers.
multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))


async def background_task():
    # this loop exits when Task.cancel() is called
    while True:
        DM.DoEvents()
        # print("DoEvents")
        await asyncio.sleep(0.1)


def get_result_image(job):
    empty = np.zeros(job.get_result_shape())
    image = DM.CreateImage(empty)
    return image


def get_result_mask_image(job):
    buffer = np.zeros(job.get_result_shape())
    image = DM.CreateImage(buffer[0])
    return (image, buffer)


async def run(executor, job, out):
    # print("run entered")
    async for tiles in executor.run_job(job):
        # print("Tiles")
        for tile in tiles:
            tile.copy_to_result(out)
        yield out
    print("Run finished")


def mask_factory_from_rect(rect, mask_shape):
    (t, l, b, r) = rect
    (y, x) = mask_shape
    t = int(max(0, t))
    l = int(max(0, l))
    b = int(min(y, b))
    r = int(min(x, r))


    def mask():
        m = np.zeros(mask_shape)
        m[int(t):int(b), int(l):int(r)] = 1
        return m
        
    return mask


async def async_main(address):
    # start background task: (can be replaced with asyncio.create_task(coro) in Python 3.7)
    GUI_events = asyncio.ensure_future(background_task())
    
    executor = await AsyncDaskJobExecutor.connect(address)

    #ds = load(
    #    "blo",
    #    path=("C:/Users/weber/Nextcloud/Projects/Open Pixelated STEM framework/"
    #    "Data/3rd-Party Datasets/Glasgow/10 um 110.blo"),
    #    tileshape=(1,8,144,144)
    #)

    ds = load(
        "raw",
        path = '/data/users/weber/scan_11_x256_y256.raw',
        dtype = "float32",
        scan_size = (256, 256),
        detector_size_raw = (130, 128),
        crop_detector_to = (128, 128)
    )

    sum_job = SumFramesJob(dataset=ds)
    (y, x) = sum_job.get_result_shape()
    sum_image = get_result_image(sum_job)
    sum_buffer = sum_image.GetNumArray()
    
    doc = DM.NewImageDocument("test document")
    r = doc.GetRootComponent()
    d = doc.AddImageDisplay(sum_image, 1)
    c = d.AddNewComponent(5, int(y * 0.4), int(x * 0.4), int(y * 0.6), int(x * 0.6))
    c.SetForegroundColor(1, 0, 0)

    doc.Show()

    async for part_result in run(executor, sum_job, sum_buffer):
        # print("Part result")
        sum_image.UpdateImage()
        
    rect = c.GetRect()
    
    mask = mask_factory_from_rect(rect, tuple(ds.shape.sig))

    rect_job = ApplyMasksJob(dataset=ds, mask_factories=[mask])
    
    result_buffer = np.zeros(rect_job.get_result_shape())
    result_image = DM.CreateImage(result_buffer[0])

    result_image.ShowImage()

    result_image_buffer = result_image.GetNumArray()
        
    counter = 0

    while counter < 20:
        counter += 1
        result_buffer[:] = 0
        async for part_result in run(executor, rect_job, result_buffer):
            np.copyto(result_image_buffer,
                # for some reason, the buffer of the image has a different shape than the original
                # numpy array to create the image
                result_buffer[0].reshape(result_image_buffer.shape), 
                casting='unsafe')
            result_image.UpdateImage()
        
        while True:
            newrect = c.GetRect()
            if newrect != rect:
                rect = newrect
                mask = mask_factory_from_rect(rect, tuple(ds.shape.sig))
                rect_job = ApplyMasksJob(dataset=ds, mask_factories=[mask])
                break
            await asyncio.sleep(1)

    GUI_events.cancel()


def main():
    cores = psutil.cpu_count(logical=False)

    if cores is None:
        cores = 2
    cluster_kwargs = {
        "threads_per_worker": 1,
        "n_workers": cores
    }

    #cluster = dd.LocalCluster(**cluster_kwargs)
    loop = asyncio.get_event_loop()
    address = 'tcp://localhost:31313'
    try:
        # (can be replaced with asyncio.run(coro) in Python 3.7)
        loop.run_until_complete(async_main(address))
        
    finally:
        # loop.close()
        print("Close cluster")
        #cluster.close()


if __name__ == "__main__":
    main()
