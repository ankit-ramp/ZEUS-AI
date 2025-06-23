'use client';

import { useEffect, useState } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const router = useRouter();
  const supabase = createClientComponentClient();

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
    };
    getUser();
  }, [supabase.auth]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/login');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Welcome to your Dashboard</h1>
        {user && (
          <div className="mb-4">
            <p className="text-gray-600">Logged in as: {user.email}</p>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Quick Links</h2>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-primary hover:text-primary/80">Company Resources</a>
              </li>
              <li>
                <a href="#" className="text-primary hover:text-primary/80">Team Calendar</a>
              </li>
              <li>
                <a href="#" className="text-primary hover:text-primary/80">Documents</a>
              </li>
            </ul>
          </div>
          <div className="bg-gray-50 p-6 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Recent Activity</h2>
            <p className="text-gray-600">No recent activity to display.</p>
          </div>
          <div className="bg-gray-50 p-6 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Account</h2>
            <button
              onClick={handleSignOut}
              className="text-red-600 hover:text-red-800"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 