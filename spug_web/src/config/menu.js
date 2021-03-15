/**
 * Created by zyupo on 2017/04/20.
 * https://github.com/openspug/spug
 */
let menu = {
    menus: [
        {
            key: '/home', desc: 'Dashboard', icon: 'fa fa-desktop', permission: 'home_view',
        },
        {
            key: '1', desc: '用户管理', icon: 'fa fa-address-card', permission: 'account_user_view|account_role_view', subs: [
                {key: '/account/user', permission: 'account_user_view', desc: '用户列表'},
                {key: '/account/role', permission: 'account_role_view', desc: '角色权限'}
            ]
        }, {
            key: '2', desc: 'worker管理', icon: 'fa fa-server', permission: 'assets_host_view|assets_host_exec_view', subs: [
                {key: '/assets/host', permission: 'assets_host_view', desc: 'worker列表'},
                {key: '/assets/host_exec', permission: 'assets_host_exec_view', desc: '批量执行'}
            ]
        },
        {
            key: '/publish/image', desc: '镜像管理', icon: 'fa fa-flag-o', permission: 'publish_app_view|publish_image_view',
        },
        {
            key: '3', desc: '任务管理', icon: 'fa fa-calendar', permission: 'job_task_view', subs: [
                {key: '/schedule/job', permission: 'job_task_view', desc: '任务列表'}
            ]
        },
        {
            key: '4', desc: '系统管理', icon: 'el-icon-setting',  permission: 'system_notify_view',  subs: [
                {key: '/system/notify', permission: 'system_notify_view', desc: '通知设置'},
            ]
        },
    ]
};

export default menu;
