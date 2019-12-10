import sys
import threading, json

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QOpenGLWidget, QApplication
import OpenGL.GL as gl
import OpenGL.GLU as glu

import objloader as obj


class GLWidget(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(QOpenGLWidget, self).__init__(parent)
        self.object = 0
        self.offset = [250.0, -50.0, 80.0]
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.z_zoom = -50
        self.xTran = 0
        self.yTran = 0
        self.lastPos = QPoint()

        # 사람
        self.person_offset = -10.0
        self.person01 = 0
        self.person02 = 0

        # 데모데이터 관련
        self.pointer01 = 1
        self.jsonfile = 'demoapp-2d50f-export.json'

        # 사람 찍기
        self.move01 = []
        self.move02 = []
        self.move03 = []
        self.move04 = []
        self.move05 = []
        self.move06 = []
        self.move07 = []
        self.move08 = []
        self.move09 = []
        self.move10 = []



    def minimumSizeHint(self):
        return QSize(100, 100)

    def sizeHint(self):
        return QSize(800, 800)

    def setXRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            self.update()

    def setYRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            self.update()

    def setZRotation(self, angle):
        self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            self.update()

    def setXYTranslate(self, dx, dy):
        self.xTran += 20 * dx
        self.yTran -= 20 * dy
        self.update()

    def setZoom(self, zoom):
        self.z_zoom = zoom
        self.update()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 2 * dy)
            self.setYRotation(self.yRot - 2 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXYTranslate(dx / 8, dy / 8)
        self.lastPos = event.pos()

    def wheelEvent(self, event):
        wheel_val = event.angleDelta().y()
        self.setZoom(self.z_zoom + 0.5 * wheel_val)

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def normalizeAngle(self, angle):
        while (angle < 0):
            angle += 360 * 16
        while (angle > 360 * 16):
            angle -= 360 * 16

    def initializeGL(self):
        # 사람 오브젝트 부르기
        self.person01 = obj.OBJ('object/per_obj.obj', swapyz=True)
        self.person02 = obj.OBJ('object/per_obj2.obj', swapyz=True)
        self.object = obj.OBJ('object/floor15.obj', swapyz=True)
        # gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_CULL_FACE)

        self.move01 = self.getJSON('test01')
        self.move02 = self.getJSON('test02')
        self.move03 = self.getJSON('test03')
        self.move04 = self.getJSON('test04')
        self.move05 = self.getJSON('test05')
        self.move06 = self.getJSON('test06')
        self.move07 = self.getJSON('test07')
        self.move08 = self.getJSON('test08')
        self.move09 = self.getJSON('test09')
        self.move10 = self.getJSON('test10')

    def drawGL(self):
        self.draw_line()
        self.setObject(1, self.object, self.offset[0], self.offset[1], self.offset[2])
        self.initializePoint()

    def setObject(self, name, object, tx, ty, tz):
        gl.glPushName(name)
        gl.glPushMatrix()
        gl.glTranslate(tx, ty, tz)
        gl.glCallList(object.gl_list)
        gl.glPopMatrix()
        gl.glPopName()

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glClearColor(255 / 255, 255 / 255, 255 / 255, 1.0)
        gl.glTranslate(0, 0, self.z_zoom)
        gl.glTranslate(self.xTran, self.yTran, 0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(-self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gl.glRotated(-90.0, 1.0, 0.0, 0.0)
        gl.glRotated(180.0, 0.0, 0.0, 1.0)
        self.drawGL()
        threading.Timer(0.2, self.setXYTranslate, (0, 0)).start()
        self.yRot += 5
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, width / height, 1.0, 10000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -2000.0)

    def draw_line(self):
        gl.glPushMatrix()
        color = [8.0 / 255, 108.0 / 255, 162.0 / 255]
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, color);
        step = 100
        num = 10
        for i in range(-num, num + 1):
            for j in range(-num, num + 1):
                gl.glBegin(gl.GL_LINES)
                gl.glVertex3f(i * step, -num * step, 0)
                gl.glVertex3f(i * step, num * step, 0)
                
                gl.glVertex3f(-num * step, i * step, 0)
                gl.glVertex3f(num * step, i * step, 0)
                
                # gl.glVertex3f(j * step, i * step, -num * step)
                # gl.glVertex3f(j * step, i * step, num * step)
                
            
                gl.glEnd()
                
        gl.glPopMatrix()
        gl.glFlush()

    def getJSON(self, test):
        ipsData = []
        json_data = open(self.jsonfile).read()
        data = json.loads(json_data)
        for key, val in enumerate(data['move_demo'][test]):
            ipsData.append(val)
        return ipsData

    def selectData(self, object, ipsData, start):
        gl.glPushMatrix()
        gl.glTranslate(ipsData[start]['x'], ipsData[start]['y'], self.person_offset)
        gl.glRotate(180, 0.0, 0.0, 1.0)
        gl.glCallList(object.gl_list)
        gl.glPopMatrix()


    def initializePoint(self):

        if self.pointer01 > 1400:
            self.pointer01 = 1
        else:
            self.pointer01 += 1
            self.selectData(self.person02, self.move01, self.pointer01)
            self.selectData(self.person01, self.move02, self.pointer01)
            self.selectData(self.person02, self.move03, self.pointer01)
            self.selectData(self.person01, self.move04, self.pointer01)
            self.selectData(self.person02, self.move05, self.pointer01)
            self.selectData(self.person01, self.move06, self.pointer01)
            self.selectData(self.person02, self.move07, self.pointer01)
            self.selectData(self.person01, self.move08, self.pointer01)
            self.selectData(self.person02, self.move09, self.pointer01)
            self.selectData(self.person01, self.move10, self.pointer01)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GLWidget()
    # window.setAutoFillBackground(True)
    window.setStyleSheet("background-color:black;")
    window.setGeometry(0.1, 0.1, 3840, 1080)
    window.show()
    sys.exit(app.exec_())
