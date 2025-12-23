'use client'
import React, { useState } from 'react';
import { auth, signOut, updatePassword } from '../../lib/firebase'; // Import from firebase.js
import { useRouter } from 'next/navigation';  // If using Next.js for navigation

const UserProfilePage = () => {
  const [newPassword, setNewPassword] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // Handle Logout
  const handleLogout = async () => {
    try {
      await signOut(auth);
      router.push('/login'); // Redirect to login page after logout
    } catch (error) {
      console.error('Error during logout:', error);
      setError('Failed to log out.');
    }
  };

  // Handle Password Change
  const handleChangePassword = async () => {
    const user = auth.currentUser;

    if (!user) {
      setError('User is not logged in.');
      return;
    }

    if (newPassword === '') {
      setError('Please enter a new password.');
      return;
    }

    try {
      setLoading(true);
      await updatePassword(user, newPassword);
      alert('Password changed successfully!');
      setLoading(false);
      setNewPassword('');  // Reset the password field
    } catch (error) {
      console.error('Error changing password:', error);
      setError('Failed to change password.');
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-4 bg-gray-50">
      <h2 className="text-2xl font-semibold mb-4">User Profile</h2>
      
      {/* Password Change Form */}
      <div className="w-full max-w-md p-4 bg-white shadow-lg rounded-lg">
        <h3 className="text-xl mb-2">Change Password</h3>
        <input
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          placeholder="Current Password"
          className="w-full p-2 mb-2 border rounded"
        />
        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder="New Password"
          className="w-full p-2 mb-2 border rounded"
        />
        <button
          onClick={handleChangePassword}
          disabled={loading}
          className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {loading ? 'Changing...' : 'Change Password'}
        </button>
        {error && <p className="text-red-600 mt-2">{error}</p>}
      </div>

      {/* Logout Button */}
      <div className="mt-6">
        <button
          onClick={handleLogout}
          className="p-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default UserProfilePage;