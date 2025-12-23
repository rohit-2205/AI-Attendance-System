import React from 'react';
import SideNave from '../_components/SideNave';
import Header from '../_components/Header';
const Layout = ({ children }) => {
  return (
    <div className="flex">
      {/* Sidebar, always visible for testing */}
      <div className="w-64 fixed hidden md:block">
        <SideNave />
      </div>

      {/* Main content */}

      <div className="ml-64 w-full ">
        <Header/>
        {children}
      </div>
    </div>
  );
};

export default Layout;
