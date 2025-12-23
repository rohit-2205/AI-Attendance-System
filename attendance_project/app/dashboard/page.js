// 'use client';

// import { useEffect, useState } from 'react';
// import { useRouter } from 'next/navigation';
// import { auth, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from '../lib/firebase';  // Adjust the path to match the file location

// import { useTheme } from "next-themes"
// import { onAuthStateChanged, signOut } from 'firebase/auth';

// export default function Dashboard() {
//   // const router = useRouter();
//   // const [user, setUser] = useState(null);
//   // const {setTheme} = useTheme()

//   useEffect(() => {
//     setTheme('light');
//     });

//   //   return () => unsubscribe();
//   // }, []);

//   // const handleLogout = async () => {
//   //   await signOut(auth);
//   //   router.push('/login');
//   // };

//   // if (!user) return null; // or a loading spinner

//   return (
//     <div className="">
//       page
//     </div>
//   );
// }


// 'use client';

// import React, { useEffect, useState } from 'react';
// import { useTheme } from 'next-themes';
// import MonthSelection from '../_components/MonthSelection';
// import GradeSelect from '../_components/GradeSelect';
// import { SunIcon, MoonIcon } from 'lucide-react'; // optional icons

// const Dashboard = () => {
//   const { theme, setTheme } = useTheme();
//   const [isMounted, setIsMounted] = useState(false);
//   const [selectedMonth, setSelectedMonth] = useState(null);
//   const [selectedGrade, setSelectedGrade] = useState(null);

//   useEffect(() => {
//     setIsMounted(true);
//   }, []);

//   const toggleTheme = () => {
//     setTheme(theme === 'dark' ? 'light' : 'dark');
//   };

//   if (!isMounted) return null; // This avoids hydration mismatch, must come after all hooks

//   return (
//     <div className="p-10">
//       <div className="flex items-center justify-between">
//         {/* Left section with heading + theme toggle */}
//         <div className="flex items-center gap-3">
//           <h2 className="font-bold text-2xl">Dashboard</h2>
//           <button
//             onClick={toggleTheme}
//             className="p-2 rounded-full border bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
//             aria-label="Toggle Theme"
//           >
//             {theme === 'dark' ? (
//               <SunIcon className="w-4 h-4 text-yellow-400" />
//             ) : (
//               <MoonIcon className="w-4 h-4 text-gray-800" />
//             )}
//           </button>
//         </div>

//         {/* Right side controls */}
//         <div className="flex items-center gap-4">
//           <MonthSelection selectedMonth={setSelectedMonth} />
//           <GradeSelect selectedGrade={setSelectedGrade} />
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Dashboard;

'use client';

import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import MonthSelection from '../_components/MonthSelection';
import GradeSelect from '../_components/GradeSelect';
import { SunIcon, MoonIcon, UsersIcon, CheckCircleIcon, XCircleIcon } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
  const { theme, setTheme } = useTheme();
  const [isMounted, setIsMounted] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [selectedGrade, setSelectedGrade] = useState(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  if (!isMounted) return null;

  const totalStudents = 120;
  const presentPercent = 75;
  const absentPercent = 25;

  const barData = [
    { name: 'Present', value: presentPercent },
    { name: 'Absent', value: absentPercent },
  ];

  const pieData = [
    { name: 'Present', value: presentPercent },
    { name: 'Absent', value: absentPercent },
  ];

  const COLORS = ['#10B981', '#EF4444'];

  return (
    <div className="p-10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="font-bold text-2xl">Dashboard</h2>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full border bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? (
              <SunIcon className="w-4 h-4 text-yellow-400" />
            ) : (
              <MoonIcon className="w-4 h-4 text-gray-800" />
            )}
          </button>
        </div>

        <div className="flex items-center gap-4">
          <MonthSelection selectedMonth={setSelectedMonth} />
          <GradeSelect selectedGrade={setSelectedGrade} />
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <Card className="bg-sky-50 p-4">
          <CardContent className="p-4 flex items-center gap-4">
            <UsersIcon className="text-sky-600 w-6 h-6" />
            <div>
              <h3 className="text-sm font-semibold">Total Students</h3>
              <p className="text-lg mt-2">{totalStudents}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-sky-50 p-4">
          <CardContent className="p-4 flex items-center gap-4">
            <CheckCircleIcon className="text-green-600 w-6 h-6" />
            <div>
              <h3 className="text-sm font-semibold">% Present</h3>
              <p className="text-lg mt-2 text-green-600">{presentPercent}%</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-sky-50 p-4">
          <CardContent className="p-4 flex items-center gap-4">
            <XCircleIcon className="text-red-500 w-6 h-6" />
            <div>
              <h3 className="text-sm font-semibold">% Absent</h3>
              <p className="text-lg mt-2 text-red-500">{absentPercent}%</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-10">
        {/* Bar Chart */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
          <h4 className="font-bold mb-4 text-sm">Attendance Bar Chart</h4>
          <BarChart width={400} height={250} data={barData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#3B82F6">
              <Cell fill="#3B82F6" />
              <Cell fill="#10B981" />
            </Bar>
          </BarChart>
        </div>

        {/* Donut Chart */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
          <h4 className="font-bold mb-4 text-sm">Monthly Overview</h4>
          <PieChart width={300} height={250}>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={5}
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

