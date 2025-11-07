#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
彻底修复导航栏用户显示问题
"""
import os
import re

def complete_navigation_fix():
    template_path = r"c:\Users\86199\Desktop\基于python二手车管理系统\templates\base.html"

    # 读取模板文件
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到整个updateNavigation函数并完全重写
    navigation_pattern = r'// 页面加载时更新导航栏和检查登录状态\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*updateNavigation\(\);\s*\}\);\s*// 更新导航栏和用户信息\s*function updateNavigation\(\) \{[\s\S]*?\}'

    new_navigation_function = """// 页面加载时更新导航栏和检查登录状态
        document.addEventListener('DOMContentLoaded', function() {
            updateNavigation();
        });

        // 更新导航栏和用户信息
        function updateNavigation() {
            const header = document.getElementById('main-header');
            const userMenu = document.getElementById('user-menu');
            const homeLink = document.getElementById('home-link');
            const sellerCenterMenu = document.getElementById('seller-center-menu');
            const token = localStorage.getItem('accessToken');

            // 如果是登录/注册页面，隐藏导航栏
            const isLoginPage = window.location.pathname === '/' ||
                               window.location.pathname.includes('/login') ||
                               window.location.pathname.includes('/register');

            if (isLoginPage) {
                header.style.display = 'none';
                return;
            } else {
                header.style.display = 'block';
            }

            // 根据用户登录状态更新首页链接
            if (homeLink) {
                if (token) {
                    // 用户已登录，首页链接指向仪表盘
                    homeLink.href = '/dashboard/';
                } else {
                    // 用户未登录，首页链接指向首页（登录页面）
                    homeLink.href = '/';
                }
            }

            // 更新用户菜单
            if (userMenu && token) {
                // 用户已登录，显示用户信息
                // 异步获取用户详细信息
                fetch('/api/users/profile/', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                    .then(response => {
                        if (response.ok) {
                            return response.json();
                        }
                        throw new Error('API failed');
                    })
                    .then(userData => {
                        const username = userData.username || '用户';
                        const avatar = userData.avatar || null;
                        // 显示卖家中心菜单
                        if (sellerCenterMenu) {
                            sellerCenterMenu.style.display = 'block';
                        }
                        // 创建用户信息界面
                        showUserInfo(username, avatar);
                    })
                    .catch(error => {
                        console.warn('获取用户信息失败，使用默认用户名:', error);
                        // 即使API失败，也显示用户菜单
                        const defaultUsername = 'User' + token.substring(0, 8);
                        // 显示卖家中心菜单
                        if (sellerCenterMenu) {
                            sellerCenterMenu.style.display = 'block';
                        }
                        // 显示用户菜单（使用默认用户名）
                        showUserInfo(defaultUsername, null);
                    });
            } else if (userMenu && !token) {
                // 用户未登录 - 彻底删除登录注册按钮，显示简单的提示信息
                userMenu.style.display = 'none';
                // 隐藏卖家中心菜单
                if (sellerCenterMenu) {
                    sellerCenterMenu.style.display = 'none';
                }
            }
        }"""

    # 替换整个updateNavigation函数
    content = re.sub(navigation_pattern, new_navigation_function, content, flags=re.MULTILINE | re.DOTALL)

    # 确保showUserInfo函数存在且正确
    show_user_info_pattern = r'function showUserInfo\(username, avatar\) \{[\s\S]*?\}'

    new_show_user_info = """function showUserInfo(username, avatar) {
            const userMenu = document.getElementById('user-menu');
            if (!userMenu) return;

            // 确保用户菜单可见
            userMenu.style.display = 'flex';

            userMenu.innerHTML = `
                <div class="user-info-container" id="user-info-container">
                    <div class="user-avatar" id="user-avatar">${avatar ? `<img src="${avatar}" alt="${username}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">` : username.charAt(0).toUpperCase()}</div>
                    <span class="user-name" id="user-name">${username}</span>
                    <span class="dropdown-arrow">▼</span>
                    <div class="user-dropdown-menu" id="user-dropdown-menu">
                        <a href="/profile/">个人中心</a>
                        <a href="/settings/">设置</a>
                        <button onclick="confirmLogout()" style="cursor: pointer;">退出账号</button>
                    </div>
                </div>
            `;

            // 设置下拉菜单点击事件
            setupUserDropdown();
        }"""

    content = re.sub(show_user_info_pattern, new_show_user_info, content, flags=re.MULTILINE | re.DOTALL)

    # 确保setupUserDropdown函数存在
    setup_dropdown_pattern = r'function setupUserDropdown\(\) \{[\s\S]*?\}'

    new_setup_dropdown = """function setupUserDropdown() {
            const container = document.getElementById('user-info-container');
            const menu = document.getElementById('user-dropdown-menu');
            if (!container || !menu) return;

            // 清除之前的事件监听器
            container.removeEventListener('click', handleDropdownClick);

            // 点击容器打开/关闭菜单
            function handleDropdownClick(e) {
                e.stopPropagation();
                container.classList.toggle('active');
                menu.classList.toggle('active');
            }

            container.addEventListener('click', handleDropdownClick);

            // 点击菜单项后关闭菜单
            const menuItems = menu.querySelectorAll('a, button');
            menuItems.forEach(item => {
                item.addEventListener('click', () => {
                    container.classList.remove('active');
                    menu.classList.remove('active');
                });
            });
        }"""

    content = re.sub(setup_dropdown_pattern, new_setup_dropdown, content, flags=re.MULTILINE | re.DOTALL)

    # 确保confirmLogout函数存在
    confirm_logout_pattern = r'function confirmLogout\(\) \{[\s\S]*?\}'

    new_confirm_logout = """function confirmLogout() {
            // 创建自定义确认对话框
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            `;

            modal.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: 8px; max-width: 400px; text-align: center;">
                    <h3 style="margin: 0 0 20px 0; color: #333;">确定要退出账号吗？</h3>
                    <div style="display: flex; gap: 15px; justify-content: center;">
                        <button id="confirm-logout" style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">确定</button>
                        <button id="cancel-logout" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">取消</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            // 确定按钮
            document.getElementById('confirm-logout').addEventListener('click', () => {
                document.body.removeChild(modal);
                logout();
            });

            // 取消按钮
            document.getElementById('cancel-logout').addEventListener('click', () => {
                document.body.removeChild(modal);
            });

            // 点击背景关闭
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    document.body.removeChild(modal);
                }
            });
        }"""

    content = re.sub(confirm_logout_pattern, new_confirm_logout, content, flags=re.MULTILINE | re.DOTALL)

    # 确保logout函数存在且正确
    logout_pattern = r'// 退出登录\s+async function logout\(\) \{[\s\S]*?\}'

    new_logout_function = """// 退出登录
        async function logout() {
            try {
                // 调用后端登出API
                const response = await fetch('/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('登出成功:', data.message);
                }
            } catch (error) {
                console.error('登出请求失败:', error);
            }

            // 清除本地存储
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('rememberMe');
            localStorage.removeItem('userInfo');

            // 重定向到首页
            window.location.href = '/';
        }"""

    content = re.sub(logout_pattern, new_logout_function, content, flags=re.MULTILINE | re.DOTALL)

    # 添加强制更新函数和调试功能
    force_update_script = """
        // 强制更新导航栏（用于调试）
        function forceUpdateNavigation() {
            console.log('强制更新导航栏');
            updateNavigation();
        }

        // 页面可见性变化时更新导航栏
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                updateNavigation();
            }
        });

        // 每隔30秒检查一次登录状态
        setInterval(updateNavigation, 30000);

        // 暴露函数到全局，供调试使用
        window.forceUpdateNavigation = forceUpdateNavigation;
        window.showUserInfo = showUserInfo;
        window.updateNavigation = updateNavigation;
        window.confirmLogout = confirmLogout;
        window.logout = logout;
        """

    # 在</script>标签之前插入强制更新脚本
    script_end_pos = content.rfind('</script>')
    if script_end_pos != -1:
        content = content[:script_end_pos] + force_update_script + '\n    </script>'

    # 写回文件
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("导航栏彻底修复完成！")
    print("1. 彻底删除了登录注册按钮的显示逻辑")
    print("2. 确保用户登录后只显示用户名、头像和下拉菜单")
    print("3. 添加了自定义退出确认对话框")
    print("4. 优化了下拉菜单的交互功能")
    print("5. 添加了强制更新和调试功能")
    return True

if __name__ == '__main__':
    complete_navigation_fix()