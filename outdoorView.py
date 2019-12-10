import sys, threading

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
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
        self.point = 0
        self.pointer = 1

        self.offset = [0.0, 0.0, 0.0]
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.z_zoom = -50
        self.xTran = 0
        self.yTran = 0
        self.lastPos = QPoint()

        self.move = []

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
        self.object = obj.OBJ('object/map.obj', swapyz=True)
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_CULL_FACE)

    def drawGL(self):
        self.draw_line()
        self.setObject(self.object, self.offset[0], self.offset[1], self.offset[2])

    def setObject(self, object, tx, ty, tz):
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
        # gl.glClearColor(12 / 255, 13 / 255, 14 / 255, 1.0)
        gl.glTranslate(0, 0, self.z_zoom)
        gl.glTranslate(self.xTran, self.yTran, 0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(-self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gl.glRotated(-90.0, 1.0, 0.0, 0.0)
        gl.glRotated(180.0, 0.0, 0.0, 1.0)
        self.drawGL()
        threading.Timer(1.0, self.setXYTranslate, (0, 0)).start()
        self.yRot += 2
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()

    def draw_line(self):
        gl.glPushMatrix()
        color = [8.0 / 255, 0.0 / 255, 0.0 / 255]
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, color);
        step = 100
        num = 5
        for i in range(-num, num + 1):
            for j in range(-num, num + 1):
                gl.glBegin(gl.GL_LINES)
                gl.glVertex3f(i * step, -num * step, j * step)
                gl.glVertex3f(i * step, num * step, j * step)
                
                gl.glVertex3f(-num * step, i * step, j * step)
                gl.glVertex3f(num * step, i * step, j * step)
                
                gl.glVertex3f(j * step, i * step, -num * step)
                gl.glVertex3f(j * step, i * step, num * step)
                
            
                gl.glEnd()
                
        gl.glPopMatrix()
        gl.glFlush()

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

    def selectData(self, object_s, x, y, start):
        gl.glPushMatrix()
        gl.glTranslate(x[start], y[start], 0.0)
        gl.glRotate(90, 0.0, 0.0, 1.0)
        gl.glRotate(90, 1.0, 0.0, 0.0)
        gl.glScale(7.0, 7.0, 7.0)
        gl.glCallList(object_s.gl_list)
        gl.glPopMatrix()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GLWidget()
    # window.setAutoFillBackground(True)
    window.setStyleSheet("background-color:white;")
    window.setGeometry(0.1, 0.1, 3840, 1080)
    window.show()
    sys.exit(app.exec_())
