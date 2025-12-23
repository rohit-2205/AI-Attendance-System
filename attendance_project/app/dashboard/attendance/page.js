'use client'
import React, { useState } from 'react';
import MonthSelection from '@/app/_components/MonthSelection';
import GradeSelect from '@/app/_components/GradeSelect';
import { Button } from '@/components/ui/button'; // ✅ Correct import

const Attendance = () => {
  const [month, setMonth] = useState(null);

  const handleMonthChange = (selectedMonth) => {
    console.log('Selected Month:', selectedMonth);
    setMonth(selectedMonth);
  };
  const[selectedMonth,setSelectedMonth]= useState();
  const[selecetdGrade, setSelectedGrade]= useState();
  const onSearchHandler=()=>{
    console.log(selectedMonth);
  }

  return (
    <div className='p-10'>
      <h2 className="text-2xl font-bold">Attendance</h2>

      <div className="flex gap-4 my-5 p-3 border rounded-lg shadow-sm">
        <div className='flex gap-2 items-center'> 
          <label >Select Month:</label>
          <MonthSelection selectedMonth={(value)=>setSelectedMonth(value)} />
        </div>

        <div className='flex gap-2 items-center'>
          <label >Select Grade:</label> {/* ✅ Fixed typo */}
          <GradeSelect   />
        </div>

        <Button onClick={()=>onSearchHandler()} className="">Search</Button>
      </div>

      {/*Student Attendance Grid here*/}
    </div>
  );
};

export default Attendance;
