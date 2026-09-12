'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { EnterpriseUser } from '@/types/platform';
import {
  Users,
  UserPlus,
  Shield,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  MoreVertical,
  Edit2,
  Trash2,
  Mail,
  Building,
  Briefcase,
  RefreshCw,
  Lock,
  Sparkles,
} from 'lucide-react';

const ROLES_LIST = ['Admin', 'Executive', 'Business Analyst', 'Data Analyst', 'Viewer'];
const DEPARTMENTS = [
  'All Departments',
  'Information Technology',
  'Executive Leadership',
  'Strategic Finance & BI',
  'Data Engineering',
  'Supply Chain & Operations',
  'Engineering',
];

export default function UsersPage() {
  const { user: currentUser, hasRole } = useAuth();
  const [users, setUsers] = useState<EnterpriseUser[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedRole, setSelectedRole] = useState('All');
  const [selectedDept, setSelectedDept] = useState('All Departments');
  const [actionNotice, setActionNotice] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<EnterpriseUser | null>(null);

  // Form states
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    job_title: '',
    department: 'Information Technology',
    phone_number: '',
    role_name: 'Business Analyst',
    is_active: true,
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      let query = `/users?page=1&page_size=50`;
      if (search) query += `&search=${encodeURIComponent(search)}`;
      if (selectedRole !== 'All') query += `&role=${encodeURIComponent(selectedRole)}`;
      if (selectedDept !== 'All Departments') query += `&department=${encodeURIComponent(selectedDept)}`;

      const res = await apiClient.get(query);
      setUsers(res.data.users || []);
      setTotalCount(res.data.total_count || 0);
    } catch (err: any) {
      console.error('Error loading users:', err);
      setActionNotice({
        message: err.response?.data?.detail || 'Failed to fetch enterprise users directory.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [selectedRole, selectedDept]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers();
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/users', formData);
      setActionNotice({ message: `Enterprise user '${formData.email}' created successfully.`, type: 'success' });
      setShowAddModal(false);
      setFormData({
        email: '',
        password: '',
        full_name: '',
        job_title: '',
        department: 'Information Technology',
        phone_number: '',
        role_name: 'Business Analyst',
        is_active: true,
      });
      fetchUsers();
    } catch (err: any) {
      setActionNotice({ message: err.response?.data?.detail || 'Failed to create user.', type: 'error' });
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await apiClient.put(`/users/${editingUser.id}`, {
        full_name: formData.full_name,
        job_title: formData.job_title,
        department: formData.department,
        phone_number: formData.phone_number,
        role_name: formData.role_name,
        is_active: formData.is_active,
      });
      setActionNotice({ message: `User '${editingUser.email}' updated successfully.`, type: 'success' });
      setShowEditModal(false);
      setEditingUser(null);
      fetchUsers();
    } catch (err: any) {
      setActionNotice({ message: err.response?.data?.detail || 'Failed to update user.', type: 'error' });
    }
  };

  const handleDeleteUser = async (userId: number, email: string) => {
    if (!confirm(`Are you sure you want to remove user '${email}' from the enterprise directory?`)) return;
    try {
      await apiClient.delete(`/users/${userId}`);
      setActionNotice({ message: `User '${email}' successfully removed.`, type: 'success' });
      fetchUsers();
    } catch (err: any) {
      setActionNotice({ message: err.response?.data?.detail || 'Failed to delete user.', type: 'error' });
    }
  };

  const openEditModal = (u: EnterpriseUser) => {
    setEditingUser(u);
    setFormData({
      email: u.email,
      password: '',
      full_name: u.full_name,
      job_title: u.job_title,
      department: u.department,
      phone_number: u.phone_number || '',
      role_name: u.roles[0]?.name || 'Viewer',
      is_active: u.is_active,
    });
    setShowEditModal(true);
  };

  const isAdmin = hasRole(['Admin']);

  if (!isAdmin) {
    return (
      <EnterpriseShell>
        <div className="bg-red-950/30 border border-red-800/60 rounded-3xl p-8 text-center max-w-2xl mx-auto my-12">
          <div className="w-14 h-14 rounded-2xl bg-red-500/10 text-red-400 flex items-center justify-center mx-auto mb-4 border border-red-500/20">
            <Lock className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Administrative Authorization Required</h2>
          <p className="text-sm text-slate-300 mb-6">
            User Management is strictly restricted to enterprise accounts with the{' '}
            <span className="font-semibold text-red-400">Admin</span> role. Your active role does not possess the requisite RBAC privileges.
          </p>
        </div>
      </EnterpriseShell>
    );
  }

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <Shield className="w-3.5 h-3.5" />
              <span>Enterprise Identity & RBAC</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise User Administration</h1>
            <p className="text-xs text-slate-400 mt-1">
              Manage enterprise identities, 5-tier role policies, organizational departments, and account statuses.
            </p>
          </div>


          <div className="flex items-center gap-3">
            <button
              onClick={fetchUsers}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Directory"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => {
                setFormData({
                  email: '',
                  password: '',
                  full_name: '',
                  job_title: '',
                  department: 'Information Technology',
                  phone_number: '',
                  role_name: 'Business Analyst',
                  is_active: true,
                });
                setShowAddModal(true);
              }}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
            >
              <UserPlus className="w-4 h-4" />
              Add Enterprise User
            </button>
          </div>
        </div>

        {/* Notice alert */}
        {actionNotice && (
          <div
            className={`p-4 rounded-2xl border text-xs flex items-center justify-between transition-all ${
              actionNotice.type === 'success'
                ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
                : 'bg-red-950/40 border-red-800/60 text-red-300'
            }`}
          >
            <div className="flex items-center gap-2">
              {actionNotice.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400 shrink-0" />
              )}
              <span>{actionNotice.message}</span>
            </div>
            <button onClick={() => setActionNotice(null)} className="text-slate-400 hover:text-white font-bold ml-4">
              &times;
            </button>
          </div>
        )}

        {/* Filters and Search Bar */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by name, email, or role..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </form>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-500">Role:</span>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="bg-transparent text-white focus:outline-none cursor-pointer"
              >
                <option value="All" className="bg-slate-900">All Roles</option>
                {ROLES_LIST.map((r) => (
                  <option key={r} value={r} className="bg-slate-900">{r}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
              <Building className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                className="bg-transparent text-white focus:outline-none cursor-pointer"
              >
                {DEPARTMENTS.map((d) => (
                  <option key={d} value={d} className="bg-slate-900">{d}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Users Data Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-5">Enterprise User</th>
                  <th className="py-3.5 px-4">Role Policy</th>
                  <th className="py-3.5 px-4">Department & Title</th>
                  <th className="py-3.5 px-4">Account Status</th>
                  <th className="py-3.5 px-4">Created Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                      Loading enterprise directory...
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      No enterprise users found matching current filters.
                    </td>
                  </tr>
                ) : (
                  users.map((u) => {
                    const primaryRole = u.roles[0]?.name || 'Viewer';
                    return (
                      <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-4 px-5">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shrink-0">
                              {u.full_name.charAt(0)}
                            </div>
                            <div>
                              <p className="font-semibold text-white">{u.full_name}</p>
                              <p className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                                <Mail className="w-3 h-3 text-slate-500" />
                                {u.email}
                              </p>
                            </div>
                          </div>
                        </td>

                        <td className="py-4 px-4">
                          <span
                            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold border ${
                              primaryRole === 'Admin'
                                ? 'bg-red-500/10 text-red-400 border-red-500/20'
                                : primaryRole === 'Executive'
                                ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                                : primaryRole === 'Business Analyst'
                                ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                : primaryRole === 'Data Analyst'
                                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                : 'bg-slate-800 text-slate-300 border-slate-700'
                            }`}
                          >
                            <Shield className="w-3 h-3" />
                            {primaryRole}
                          </span>
                        </td>

                        <td className="py-4 px-4">
                          <p className="text-slate-200 font-medium">{u.department || 'General'}</p>
                          <p className="text-[11px] text-slate-400">{u.job_title || 'Enterprise User'}</p>
                        </td>

                        <td className="py-4 px-4">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                              u.is_active
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-slate-800 text-slate-500 border border-slate-700'
                            }`}
                          >
                            {u.is_active ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                            {u.is_active ? 'ACTIVE' : 'DEACTIVATED'}
                          </span>
                        </td>

                        <td className="py-4 px-4 text-slate-400 text-[11px]">
                          {new Date(u.created_at).toLocaleDateString()}
                        </td>

                        <td className="py-4 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => openEditModal(u)}
                              className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-blue-400 rounded-lg transition-colors"
                              title="Edit User Profile"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeleteUser(u.id, u.email)}
                              disabled={u.email === currentUser?.email}
                              className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-red-400 rounded-lg transition-colors disabled:opacity-30"
                              title={u.email === currentUser?.email ? "Cannot delete self" : "Delete User"}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add User Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2">
                  <UserPlus className="w-5 h-5 text-blue-500" />
                  <h3 className="text-base font-bold text-white">Create Enterprise Account</h3>
                </div>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-slate-400 hover:text-white text-lg font-bold"
                >
                  &times;
                </button>
              </div>

              <form onSubmit={handleCreateUser} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Corporate Email</label>
                  <input
                    type="email"
                    required
                    placeholder="user@aegisiq.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Initial Password</label>
                  <input
                    type="password"
                    required
                    placeholder="Minimum 8 characters"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Full Name</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Rachel Adams"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Job Title</label>
                    <input
                      type="text"
                      placeholder="e.g. Senior Data Analyst"
                      value={formData.job_title}
                      onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Assigned Role</label>
                    <select
                      value={formData.role_name}
                      onChange={(e) => setFormData({ ...formData, role_name: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    >
                      {ROLES_LIST.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Department</label>
                    <select
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    >
                      {DEPARTMENTS.filter(d => d !== 'All Departments').map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20"
                  >
                    Create Account
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit User Modal */}
        {showEditModal && editingUser && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2">
                  <Edit2 className="w-5 h-5 text-blue-500" />
                  <h3 className="text-base font-bold text-white">Edit User: {editingUser.email}</h3>
                </div>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="text-slate-400 hover:text-white text-lg font-bold"
                >
                  &times;
                </button>
              </div>

              <form onSubmit={handleUpdateUser} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Full Name</label>
                    <input
                      type="text"
                      required
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Job Title</label>
                    <input
                      type="text"
                      value={formData.job_title}
                      onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Assigned Role</label>
                    <select
                      value={formData.role_name}
                      onChange={(e) => setFormData({ ...formData, role_name: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    >
                      {ROLES_LIST.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Department</label>
                    <select
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                    >
                      {DEPARTMENTS.filter(d => d !== 'All Departments').map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Account Active Status</label>
                  <div className="flex items-center gap-4 pt-1">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={formData.is_active === true}
                        onChange={() => setFormData({ ...formData, is_active: true })}
                        className="text-blue-600 focus:ring-0"
                      />
                      <span className="text-emerald-400 font-semibold">Active Account</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={formData.is_active === false}
                        onChange={() => setFormData({ ...formData, is_active: false })}
                        className="text-red-600 focus:ring-0"
                      />
                      <span className="text-red-400 font-semibold">Deactivated / Suspended</span>
                    </label>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowEditModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </EnterpriseShell>
  );
}
