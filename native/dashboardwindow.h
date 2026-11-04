// SPDX-FileCopyrightText: 2026 Yung-Ting Chen
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <QPointer>
#include <QQuickWindow>
#include <QQuickItem>

class DashboardWindow : public QQuickWindow
{
    Q_OBJECT
    Q_PROPERTY(QQuickItem *mainItem READ mainItem WRITE setMainItem NOTIFY mainItemChanged)
    Q_PROPERTY(QQuickItem *visualParent READ visualParent WRITE setVisualParent NOTIFY visualParentChanged)
    Q_PROPERTY(QQuickItem *keyEventProxy READ keyEventProxy WRITE setKeyEventProxy NOTIFY keyEventProxyChanged)
    Q_PROPERTY(QColor backgroundColor READ color WRITE setColor NOTIFY backgroundColorChanged)
public:
    explicit DashboardWindow(QWindow *parent = nullptr);
    QQuickItem *mainItem() const { return m_mainItem; }
    void setMainItem(QQuickItem *item);
    QQuickItem *visualParent() const { return m_visualParent; }
    void setVisualParent(QQuickItem *item);
    QQuickItem *keyEventProxy() const { return m_keyEventProxy; }
    void setKeyEventProxy(QQuickItem *item);
    Q_INVOKABLE void toggle();
public Q_SLOTS:
    void closeForDesktopChange();
Q_SIGNALS:
    void backgroundColorChanged();
    void mainItemChanged();
    void visualParentChanged();
    void keyEventProxyChanged();
    void keyEscapePressed();
protected:
    bool event(QEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;
private:
    void syncScreen();
    QPointer<QQuickItem> m_mainItem;
    QPointer<QQuickItem> m_visualParent;
    QPointer<QQuickItem> m_keyEventProxy;
    QMetaObject::Connection m_parentScreenConnection;
    QMetaObject::Connection m_parentWindowConnection;
    static QPointer<DashboardWindow> s_openWindow;
};
