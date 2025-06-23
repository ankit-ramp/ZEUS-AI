import React from 'react';
import FileUploader from '@/components/FileUploader';

const Page: React.FC = () => {
  return (
    <>
    <div className="Title px-6 flex  items-start justify-between gap-4 py-8 text-start">
      <div className="flex flex-col gap-4">
      <h1 className="text-4xl playfair  ">PO data extraction using AI</h1>
      <h2 className="text-md">Upload your po files and get excel file in return with with the help of AI</h2></div>
      
      {/* <div>
        <button className="bg-emerald-800 py-6 px-2">Tabular report</button>
      </div> */}
    </div>
      <div className="fileupload w-full bg-slate-100 min-h-94 py-4 px-4 flex flex-col md:flex-row items-center justify-center ">
          <FileUploader actionUrl="/api/proxy/upload" />
      </div>
    </>
    
  );
};

export default Page;
