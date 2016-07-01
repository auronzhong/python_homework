import os.path
import string

ext_list = ['.bak', '.trn', '.txt', '.png', '.html', '.gif', '.jpg']


def autozip(directory):
    os.path.walk(directory, walk_callback, '')


def walk_callback(args, directory, files):
    print 'Scanning', directory
    for fileName in files:
        if os.path.isfile(os.path.join(directory, fileName)) and string.lower(
                os.path.splitext(fileName)[1]) in ext_list:
            zipMyFile(os.path.join(directory, fileName))


def zipMyFile(fileName):
    os.chdir(os.path.dirname(fileName))
    zipFilename = os.getcwd().split("/")[-1] + ".zip"
    print ' Zipping to ' + zipFilename
    print 'zip -mj9 "' + zipFilename + '" "' + os.path.basename(fileName) + '"'
    os.system('zip -mj9 "' + zipFilename + '" "' + os.path.basename(fileName) + '"')

# autozip(r'./data/1')
# print "All done."
