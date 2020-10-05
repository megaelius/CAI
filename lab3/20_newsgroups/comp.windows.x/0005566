Can anybody help me?
I am having a problem displaying images greater than 32768 bytes on a Sparc
IPC running Openwindows 3.0 and dni. My program runs on a Vax and displays
images on the IPC with no problems if I use Openwindows 2.0. The program uses
the following lines to display the image - it is the XPutImage() routine
that crashes.
	XImage          *ximage;
	ximage = XCreateImage(myDisplay, DefaultVisual(myDisplay, myScreen),
			      ddepth, ZPixmap, 0, image,
			      xwid, ywid, 8, 0);
	XPutImage(myDisplay, myWindow, myGC, ximage, 0, 0,
		  xpos, ypos, xwid, ywid);
The error I get is:-
XIO:  fatal IO error 65535  on X server "galaxy::0.0"
      after 30 requests (18 known processed) with 0 events remaining.
%XLIB-F-IOERROR, xlib io error
-SYSTEM-F-LINKDISCON, network partner disconnected logical link
%TRACE-F-TRACEBACK, symbolic stack dump follows
module name     routine name                     line       rel PC    abs PC
MYXSUBS         my_imtoiks                       3184      00000093  000010AF
TEST            main                              293      000000E5  00000EE5
I have a simple test program if anyone would like to test it !!
Thanks Paul.
| Paul Jaques                                                               |
| Systems Engineer, Camborne School of Mines,                               |
|                   Rosemanowes, Herniss, Penryn, Cornwall.                 |
| E-Mail: pjaques@csm.ac.uk Tel: Stithians (0209) 860141 Fax: (0209) 861013 |
