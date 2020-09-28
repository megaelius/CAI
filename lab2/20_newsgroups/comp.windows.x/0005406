I am using the GLX widget + athena widgets on a mixed-model
application, under 4Dwm, but when the dialog gets popped up, its
text entry field does not have focus. Aimilar code works perfectly if
I use "pure X" (no mixed-model). HEre is the relevant portion of
the code.
   int n;
   Arg wargs[16];
   Widget Button, PopUpShell, Dialog;
   /* initialize TopLevel here */
   XtSetArg(wargs[n], XtNlabel, "Foo"); n++;
   Button = XtCreateManagedWidget("FooBtn", commandWidgetClass,
                                  TopLevel, wargs, n);
   PopUpShell = XtCreatePopupShell("PupShell", overrideShellWidgetClass,
                                   Button, NULL, 0);
   XtAddCallback(PopUpShell, XtNcallback, MyPopUp, (XtPointer)PopUpShell);
   XtSetArg(wargs[n], XtNvalue, ""); n++;
   Dialog = XtCreateManagedWidget("TheDialog", dialogWidgetClass,
                                  PopUpShell, wargs, n);
void MyPopUp(w, popup_shell, call_data)
Widget w;
Widget popup_shell;
XtPointer call_data;
   XtPopup(popup_shell, XtGrabExclusive);
A way I found to give focus to the text field is to move the
application window around a little bit and place it right behind the popup.
Any pointers would be greatly appreciated.
