#pragma once

#include <QtWidgets/QMainWindow>
#include "ui_Qtnew.h"

class Qtnew : public QMainWindow
{
    Q_OBJECT

public:
    Qtnew(QWidget *parent = nullptr);
    ~Qtnew();

private:
    Ui::QtnewClass ui;
};
