#ifndef QSTKEARTH_H
#define QSTKEARTH_H

#include "STK.h"
#include <QWidget>
#include <ActiveQt/QAxWidget>
#include <QMutexLocker>
#include <QDebug>
#include "stdafx.h"

class QSTKEarth : public QWidget
{
    Q_OBJECT
public:
    static QSTKEarth& getInstance()
    {
        if (instance == NULL)
        {
            QMutexLocker locker(&mutex);
            if (NULL == instance)
                instance = new QSTKEarth;
        }
        return *instance;
    }
    bool enableControl;
    ~QSTKEarth();
private:
    static QMutex mutex;
    static QAtomicPointer<QSTKEarth> instance;
    QSTKEarth(const QSTKEarth&);
    QSTKEarth(QWidget* parent = 0);
    IAgStkObjectRootPtr  m_pRoot;
    IAgSTKXApplicationPtr m_app;

public:
    void PauseSTK();
    void StartSTK();
    void FasterSTK();
    void SlowerSTK();
    void ResetSTK();
    void NewScenario();
    void LoadScenario();
    void UnloadStkScence();

};
#endif // QSTKEARTH_H
