from byuam import Department
from byugui.publish_gui import PublishWindow
from PyQt4 import QtGui
import os
import nuke

nuke_publish_dialog = None

def go():
    parent = QtGui.QApplication.activeWindow()
    filepath = nuke.toNode("root").name() #grab name of file they're working on
    global nuke_publish_dialog
    nuke_publish_dialog = PublishWindow(filepath, parent, [Department.COMP])
    nuke_publish_dialog.finished.connect(post_publish)

def post_publish():
    element = nuke_publish_dialog.result

    if nuke_publish_dialog.published:
        #if the file hasn't been saved, save it
        #if not cmds.file(q=True, sceneName=True) == '':
        #    cmds.file(save=True, force=True) #save file

        #Publish
        user = nuke_publish_dialog.user
        src = nuke_publish_dialog.src
        comment = nuke_publish_dialog.comment
        dst = element.publish(user, src, comment)
        #Ensure file has correct permissions
        try:
            os.chmod(dst, 0660)
        except:
            pass

        print "TODO: export playblast"
        print nuke_publish_dialog.result.get_name()

        #print "Exporting Alembic"
        #alembic_static_exporter.go()

