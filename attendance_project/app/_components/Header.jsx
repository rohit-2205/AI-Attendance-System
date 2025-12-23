'use client'
import React from 'react'
import Image from 'next/image';
import useFirebaseBrowserClient from '../lib/useFirebaseBrowserClient'; 

const Header = () => {
  const { user } = useFirebaseBrowserClient();

  return (
    <div className='p-4 shadow-sm border flex justify-between items-center'>
      <div className="">
        {/* Add logo or site title here if needed */}
      </div>
      <div className="">
        {user && (
          <div className="flex items-center gap-3 ">
            {user?.picture ? (
              <Image 
                src={user.picture} 
                width={40} 
                height={40} 
                alt="User" 
                className="rounded-full object-cover"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-gray-500 flex items-center justify-center text-white text-sm">
                {user.displayName?.charAt(0)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Header;
