import { useState } from 'react'; // Only import useState if you're using it
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "@/components/ui/select"
  


const AddNewStudent = () => {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button onClick={() => setOpen(true)} className='bg-blue-700 text-white hover:bg-blue-800'>
          + Add New Student
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Student</DialogTitle>
          <DialogDescription>
            <div className="py-2">
                <label htmlFor="">Full Name</label>
                <Input placeholder='Ex. Rohit Gakhare'/>
            </div>
            <div className="flex flex-col py-2">
                <label htmlFor="">Select Class</label>
                <select className='p-3 border rounded-lg ' name="" id="">
                    <option value={'A'}> A</option>
                    <option value={'B'}> B</option>
                </select>
            </div>
            <div className="py-2">
                <label htmlFor="">Contact Number</label>
                <Input type="number" placeholder='Ex. 9637585940'/>
            </div>
            <div className="py-2">
                <label htmlFor="">Address</label>
                <Input placeholder='Ex. At.Post Sawali(Bk.) Tah.Karanja(Gh)'/>
            </div>
            <div className="flex gap-3 items-center justify-end my-5 mt-5">
                <Button  onClick={()=>setOpen(false)} variant='ghost'>Cancel</Button>
                <Button className='bg-blue-700 text-white hover:bg-blue-800'  onClick={()=>console.log(save)}>Save</Button>
            </div>

          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}

export default AddNewStudent;
