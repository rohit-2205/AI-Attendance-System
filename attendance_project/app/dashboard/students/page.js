'use client'

import React from 'react'
import AddNewStudent from './_components/AddNewStudent'

const page = () => {
  return (
    <div className='p-7'>
      {/* Wrap heading and button in a flex container */}
      <div className="flex justify-between items-center p-4">
        <h2 className="font-bold text-2xl text-black">Students</h2>
        <AddNewStudent />
      </div>
    </div>
  )
}

export default page
