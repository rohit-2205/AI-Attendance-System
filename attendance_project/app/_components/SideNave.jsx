'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { GraduationCap, Hand, LayoutIcon, Settings } from 'lucide-react';
import useFirebaseBrowserClient from '../lib/useFirebaseBrowserClient'; // make sure this path is correct

const SideNave = () => {
  const { user } = useFirebaseBrowserClient();

  const menuList = [
    {
      id: 1,
      name: 'Dashboard',
      icon: LayoutIcon,
      path: '/dashboard',
    },
    {
      id: 2,
      name: 'Students',
      icon: GraduationCap,
      path: '/dashboard/students',
    },
    {
      id: 3,
      name: 'Attendance',
      icon: Hand,
      path: '/dashboard/attendance',
    },
    {
      id: 4,
      name: 'Settings',
      icon: Settings,
      path: '/dashboard/dash_settings',
    },
  ];

  return (
    <div className="border shadow-md h-screen p-5 flex flex-col justify-between">
      <div>
          <Image 
      src="/Upasthit.svg" 
      alt="Logo" 
      width={180}  
      height={50}  
    />


        <hr className="my-5" />

        {menuList.map((menu) => (
          <Link href={menu.path} key={menu.id}>
            <div className="flex items-center gap-3 text-md p-4 text-slate-500 hover:bg-indigo-500 hover:text-white rounded-lg transition my-2 cursor-pointer">
              <menu.icon className="w-5 h-5" />
              <span>{menu.name}</span>
            </div>
          </Link>
        ))}
      </div>

      {user && (
        <div className="flex items-center gap-3 p-4">
          {user?.picture ? (
            <Image 
              src={user?.picture} 
              width={40} 
              height={40} 
              alt="User" 
              className="rounded-full object-cover"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-gray-500 flex items-center justify-center text-white text-sm">
              {user?.displayName?.charAt(0)}
            </div>
          )}
          <span className="text-sm text-slate-700">{user.displayName?.split(' ')[0]}</span>
        </div>
      )}
    </div>
  );
};

export default SideNave;
