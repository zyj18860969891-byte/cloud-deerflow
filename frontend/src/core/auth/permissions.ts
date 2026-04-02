/**
 * Permission checking utilities
 * 
 * 提供简单的权限检查功能，基于用户角色和资源权限
 */

/**
 * 用户类型定义
 */
export interface User {
  id: string;
  email: string;
  name?: string;
  roles?: string[];
  permissions?: string[];
  [key: string]: unknown;
}

/**
 * 检查用户是否具有指定角色
 * 
 * @param user - 用户对象或Session
 * @param role - 要检查的角色
 * @returns 是否具有该角色
 */
export function hasRole(user: User | null | undefined, role: string): boolean {
  if (!user) return false;
  
  // 检查用户角色
  if (user.roles && Array.isArray(user.roles)) {
    return user.roles.includes(role);
  }
  
  // 检查用户.role字段（单个角色）
  if (user.role === role) {
    return true;
  }
  
  // 检查用户权限字段
  if (user.permissions && Array.isArray(user.permissions)) {
    return user.permissions.includes(role);
  }
  
  return false;
}

/**
 * 检查用户是否具有任意一个指定角色
 * 
 * @param user - 用户对象或Session
 * @param roles - 角色列表
 * @returns 是否具有任意一个角色
 */
export function hasAnyRole(user: User | null | undefined, roles: string[]): boolean {
  return roles.some(role => hasRole(user, role));
}

/**
 * 检查用户是否具有所有指定角色
 * 
 * @param user - 用户对象或Session
 * @param roles - 角色列表
 * @returns 是否具有所有角色
 */
export function hasAllRoles(user: User | null | undefined, roles: string[]): boolean {
  return roles.every(role => hasRole(user, role));
}

/**
 * 检查用户是否为管理员
 * 
 * @param user - 用户对象或Session
 * @returns 是否为管理员
 */
export function isAdmin(user: User | null | undefined): boolean {
  return hasRole(user, 'admin') || hasRole(user, 'superadmin');
}

/**
 * 检查用户是否具有数据库优化权限
 * 
 * @param user - 用户对象或Session
 * @returns 是否具有数据库优化权限
 */
export function canAccessDatabaseOptimization(user: User | null | undefined): boolean {
  // 只有管理员可以访问数据库优化功能
  return isAdmin(user);
}

/**
 * 获取用户可访问的功能模块
 * 
 * @param user - 用户对象或Session
 * @returns 可访问的功能模块列表
 */
export function getAllowedModules(user: User | null | undefined): string[] {
  const modules: string[] = ['dashboard']; // 所有登录用户都可以访问仪表板
  
  if (isAdmin(user)) {
    modules.push('database-optimization', 'admin-panel', 'user-management');
  }
  
  return modules;
}

/**
 * 检查用户是否有权访问指定模块
 * 
 * @param user - 用户对象或Session
 * @param module - 模块名称
 * @returns 是否有权访问
 */
export function canAccessModule(user: User | null | undefined, module: string): boolean {
  const allowedModules = getAllowedModules(user);
  return allowedModules.includes(module);
}