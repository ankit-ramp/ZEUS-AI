'use client';

import { useState, ChangeEvent } from 'react';
import { FaFilePdf, FaFileCsv, FaUpload, FaSpinner, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

export default function ParseOrdersPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parsedCsvData, setParsedCsvData] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setParsedCsvData(null);
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        setFileName(file.name);
      } else {
        setError('Invalid file type. Please upload a PDF.');
        setSelectedFile(null);
        setFileName('');
        event.target.value = ''; // Reset file input
      }
    }
  };

  const handleParse = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file first.');
      return;
    }
    setIsParsing(true);
    setError(null);
    setParsedCsvData(null);

    // Simulate API call for parsing
    await new Promise(resolve => setTimeout(resolve, 2000)); 

    // --- Replace with actual API call --- 
    // const formData = new FormData();
    // formData.append('pdf_file', selectedFile);
    // try {
    //   const response = await fetch('/api/parse-pdf', { // Your backend API endpoint
    //     method: 'POST',
    //     body: formData,
    //   });
    //   if (!response.ok) {
    //     const errData = await response.json();
    //     throw new Error(errData.message || 'Failed to parse PDF.');
    //   }
    //   const csvData = await response.text(); // Assuming your API returns CSV as text
    //   setParsedCsvData(csvData);
    // } catch (err: any) {
    //   setError(err.message || 'An unknown error occurred during parsing.');
    // }
    // --- End of placeholder for API call ---

    // Placeholder success
    const mockCsvData = "Order ID,Product Name,Quantity,Price\n1001,Super Widget,2,19.99\n1002,Mega Gadget,1,49.50\n1003,Basic Thing,5,5.25";
    setParsedCsvData(mockCsvData);
    // setError('This is a simulated error after parsing.'); // Uncomment to test error display

    setIsParsing(false);
  };

  const handleDownload = () => {
    if (!parsedCsvData) return;
    const blob = new Blob([parsedCsvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    const originalFileName = fileName.substring(0, fileName.lastIndexOf('.')) || 'parsed_orders';
    link.setAttribute('download', `${originalFileName}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-4 md:p-8 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-slate-800 shadow-2xl rounded-lg p-6 md:p-10">
        <div className="text-center mb-8">
          <FaFilePdf className="mx-auto text-sky-400 text-5xl mb-4" />
          <h1 className="text-3xl font-bold text-sky-400">Parse Order PDF</h1>
          <p className="text-slate-400 mt-2">Upload your order PDF to convert it into a downloadable CSV file.</p>
        </div>

        {/* File Upload Section */}
        <div className="mb-6">
          <label 
            htmlFor="pdf-upload"
            className="w-full flex flex-col items-center px-4 py-6 bg-slate-700 text-slate-300 rounded-lg shadow-md tracking-wide uppercase border-2 border-dashed border-slate-600 cursor-pointer hover:bg-slate-600 hover:text-sky-300 transition-colors duration-150"
          >
            <FaUpload className="text-3xl mb-2" />
            <span className="text-base leading-normal">{fileName || 'Select a PDF file'}</span>
            <input id="pdf-upload" type="file" className="hidden" accept=".pdf" onChange={handleFileChange} />
          </label>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-3 bg-red-700/30 text-red-400 border border-red-600 rounded-md flex items-center">
            <FaTimesCircle className="mr-2 text-red-400" />
            <p>{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <button
            onClick={handleParse}
            disabled={!selectedFile || isParsing}
            className="w-full sm:w-auto flex-grow flex items-center justify-center px-6 py-3 bg-sky-600 text-white font-semibold rounded-lg shadow-md hover:bg-sky-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-slate-800"
          >
            {isParsing ? (
              <>
                <FaSpinner className="animate-spin mr-2" /> Parsing...
              </>
            ) : (
              <>
                <FaFilePdf className="mr-2" /> Parse PDF to CSV
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            disabled={!parsedCsvData || isParsing}
            className="w-full sm:w-auto flex-grow flex items-center justify-center px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg shadow-md hover:bg-emerald-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-slate-800"
          >
            <FaFileCsv className="mr-2" /> Download CSV
          </button>
        </div>

        {/* Parsed Data Confirmation (Optional) */}
        {parsedCsvData && !error && !isParsing && (
            <div className="p-4 bg-emerald-700/30 text-emerald-300 border border-emerald-600 rounded-md flex items-center">
                <FaCheckCircle className="mr-3 text-3xl text-emerald-400" />
                <div>
                    <h3 className="font-semibold">Parsing Successful!</h3>
                    <p className="text-sm">Your CSV file is ready for download.</p>
                </div>
            </div>
        )}
      </div>

      <div className="mt-8 text-center text-sm text-slate-500">
        <p>Ensure your PDF is in a parsable format. Processing times may vary.</p>
      </div>
    </div>
  );
}
