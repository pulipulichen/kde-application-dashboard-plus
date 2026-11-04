// SPDX-FileCopyrightText: 2026 Yung-Ting Chen
// SPDX-License-Identifier: GPL-3.0-or-later
#include "dashboardwindow.h"
#include <QCoreApplication>
#include <QKeyEvent>
#include <QQuickItem>
#include <QScreen>
#include <KWindowEffects>
#include <KWindowSystem>
#include <KX11Extras>

QPointer<DashboardWindow> DashboardWindow::s_openWindow;

DashboardWindow::DashboardWindow(QWindow *parent) : QQuickWindow(parent)
{
    setFlags(Qt::Window | Qt::FramelessWindowHint);
    // Every applet in plasmashell shares this native plugin, including applets
    // loaded by different QQmlEngines. No timers or persistent lock files.
    connect(this, &QQuickWindow::colorChanged, this, &DashboardWindow::backgroundColorChanged);
    connect(KX11Extras::self(), &KX11Extras::currentDesktopChanged,
            this, &DashboardWindow::closeForDesktopChange);
}

void DashboardWindow::setMainItem(QQuickItem *item)
{
    if (m_mainItem == item) return;
    if (m_mainItem) m_mainItem->setParentItem(nullptr);
    m_mainItem = item;
    if (item) item->setParentItem(contentItem());
    Q_EMIT mainItemChanged();
}

void DashboardWindow::setVisualParent(QQuickItem *item)
{
    if (m_visualParent == item) return;
    disconnect(m_parentScreenConnection);
    disconnect(m_parentWindowConnection);
    m_visualParent = item;
    if (item) {
        auto bindWindow = [this]() {
            disconnect(m_parentScreenConnection);
            if (m_visualParent && m_visualParent->window()) {
                m_parentScreenConnection = connect(m_visualParent->window(), &QWindow::screenChanged,
                                                   this, [this]() { syncScreen(); });
            }
            syncScreen();
        };
        m_parentWindowConnection = connect(item, &QQuickItem::windowChanged, this, bindWindow);
        bindWindow();
    }
    Q_EMIT visualParentChanged();
}

void DashboardWindow::setKeyEventProxy(QQuickItem *item)
{
    if (m_keyEventProxy == item) return;
    m_keyEventProxy = item;
    Q_EMIT keyEventProxyChanged();
}

void DashboardWindow::syncScreen()
{
    QScreen *target = m_visualParent && m_visualParent->window()
        ? m_visualParent->window()->screen() : screen();
    if (target) {
        setScreen(target);
        setGeometry(target->geometry());
    }
}

void DashboardWindow::toggle()
{
    if (isVisible()) {
        hide();
    } else {
        syncScreen();
        showFullScreen();
        // Match Plasma 5's X11 activation, without ever re-activating on FocusOut.
        if (KWindowSystem::isPlatformX11()) KX11Extras::forceActiveWindow(winId());
        else requestActivate();
    }
}

void DashboardWindow::closeForDesktopChange()
{
    if (isVisible()) hide();
}

bool DashboardWindow::event(QEvent *e)
{
    if (e->type() == QEvent::Show) {
        if (s_openWindow && s_openWindow != this) s_openWindow->hide();
        s_openWindow = this;
        if (KWindowSystem::isPlatformX11()) {
            KX11Extras::setOnDesktop(winId(), KX11Extras::currentDesktop());
            KWindowSystem::setType(winId(), NET::Normal);
            KWindowSystem::setState(winId(), NET::SkipTaskbar | NET::SkipPager | NET::SkipSwitcher);
            KWindowEffects::enableBlurBehind(this, true);
        }
        if (m_keyEventProxy) m_keyEventProxy->forceActiveFocus(Qt::OtherFocusReason);
    } else if (e->type() == QEvent::Hide && s_openWindow == this) {
        s_openWindow.clear();
    }
    // In particular, leave FocusOut alone: IME candidate windows may take focus.
    return QQuickWindow::event(e);
}

void DashboardWindow::keyPressEvent(QKeyEvent *e)
{
    const bool composing = m_keyEventProxy && m_keyEventProxy->property("inputMethodComposing").toBool();
    if (e->key() == Qt::Key_Escape && !composing) {
        Q_EMIT keyEscapePressed();
        e->accept();
        return;
    }
    // Continue typing after navigating a grid. Keep focus in the real editor;
    // do not use the original hidden-editor / processEvents / restore-focus hack.
    const bool textKey = !e->text().isEmpty() && e->text().at(0).isPrint();
    if (m_keyEventProxy && !m_keyEventProxy->hasActiveFocus()
        && (textKey || e->key() == Qt::Key_Backspace)
        && !(e->modifiers() & (Qt::ControlModifier | Qt::AltModifier | Qt::MetaModifier))) {
        m_keyEventProxy->forceActiveFocus(Qt::OtherFocusReason);
        QKeyEvent copy(e->type(), e->key(), e->modifiers(), e->nativeScanCode(),
                       e->nativeVirtualKey(), e->nativeModifiers(), e->text(), e->isAutoRepeat(), e->count());
        QCoreApplication::sendEvent(this, &copy);
        e->accept();
        return;
    }
    QQuickWindow::keyPressEvent(e);
}
