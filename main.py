import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import socket
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', default='', type=str)
args = parser.parse_args()

demo = args.host == ''
if not demo:
    remote_addr = (args.host, 8888)

if demo:
    sock = None
else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

win = pg.GraphicsWindow()
win.setWindowTitle('EMG Traces')

num_plots = 16
plots = []
curves = []
for i in range(num_plots):
    if i % np.sqrt(num_plots) == 0:
        win.nextRow()
    plots.append(win.addPlot())
    plots[i].setDownsampling(mode='peak')
    plots[i].setClipToView(True)
    data = np.random.normal(size=200)
    curves.append(plots[i].plot(data))

current_data_view = None
def update():
    global current_data_view, curves
    if not demo:
        data = sock.recv(2 ** 13) # blocks until data?
        data = json.loads(data.decode('utf-8'))
        data = np.array([i['sample'] for i in data['emgMcs']])
    else:
        data = np.random.random((150, 16))
    if current_data_view is None:
        current_data_view = data
    elif current_data_view.shape[0] < 3000:
        current_data_view = np.vstack((current_data_view, data))
    else:
        current_data_view = np.roll(current_data_view, -data.shape[0], axis=0)
        current_data_view[-data.shape[0]:,:] = data
    for counter, c in enumerate(curves):
        c.setData(y=current_data_view[:, counter])

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
if not demo:
    sock.sendto(b'start', remote_addr)
timer.start(16)

if __name__ == '__main__':
    import sys
    try:
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
    finally:
        if not demo:
            sock.sendto(b'stop', remote_addr)
            sock.close()