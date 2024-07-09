#include "stdafx.h"
#include "Qtnew.h"
#include <QtWidgets/QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Qtnew w;
    w.show();
    return a.exec();
}
