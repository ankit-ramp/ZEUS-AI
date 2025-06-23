'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { createClientComponentClient, User } from '@supabase/auth-helpers-nextjs';
import { FaHome, FaUser, FaSignOutAlt, FaRobot, FaChevronDown, FaChevronUp, FaBrain, FaBullhorn, FaShoppingCart, FaFileInvoiceDollar, FaHeadset, FaUserCircle, FaSignInAlt } from 'react-icons/fa';

interface SubMenuItem {
  name: string;
  href: string;
}

interface MenuItem {
  name: string;
  href?: string;
  icon: React.ElementType;
  subItems?: SubMenuItem[];
  requiresAuth?: boolean;
}

const mainNavItems: MenuItem[] = [
  { name: 'AI', icon: FaBrain, subItems: [
    { name: 'Coming Soon', href: '/dashboard/ai/analytics' },
    // { name: 'AI Chatbot', href: '/dashboard/ai/chatbot' },
    // { name: 'AI Automation', href: '/dashboard/ai/automation' },
  ], requiresAuth: true },
  { name: 'CRM', icon: FaBullhorn, subItems: [
    { name: 'Enquiries', href: '/dashboard/crm/enquiries' },
    // { name: 'Deals', href: '/dashboard/crm/deals' },
    // { name: 'Tasks', href: '/dashboard/crm/tasks' },
  ], requiresAuth: true },
  { name: 'Purchase', icon: FaShoppingCart, subItems: [
    { name: 'Parse Orders', href: '/dashboard/purchase/parse-orders' },
    { name: 'Process PO\'s', href: '/dashboard/purchase/po' },
    // { name: 'Invoices', href: '/dashboard/purchase/invoices' },
  ], requiresAuth: true },
  
  // { name: 'Finance', icon: FaFileInvoiceDollar, subItems: [
  //   { name: 'Budgets', href: '/dashboard/finance/budgets' },
  //   { name: 'Expenses', href: '/dashboard/finance/expenses' },
  //   { name: 'Reports', href: '/dashboard/finance/reports' },
  // ], requiresAuth: true },
  { name: 'Support', icon: FaHeadset, subItems: [
    // { name: 'Tickets', href: '/dashboard/support/tickets' },
    { name: 'Knowledge Base', href: '/dashboard/support/kb' },
    { name: 'FAQ', href: '/dashboard/support/faq' },
  ], requiresAuth: false },
];

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClientComponentClient();
  const userDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const getUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setCurrentUser(session?.user ?? null);
    };
    getUser();
    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      setCurrentUser(session?.user ?? null);
      if (event === 'SIGNED_OUT') {
        setIsUserDropdownOpen(false);
      }
    });
    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, [supabase, pathname]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userDropdownRef.current && !userDropdownRef.current.contains(event.target as Node)) {
        setIsUserDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setCurrentUser(null);
    setOpenDropdown(null);
    setIsUserDropdownOpen(false);
    router.push('/login');
    router.refresh();
  };

  const toggleMainDropdown = (itemName: string) => {
    setOpenDropdown(openDropdown === itemName ? null : itemName);
    setIsUserDropdownOpen(false);
  };

  const toggleUserDropdown = () => {
    setIsUserDropdownOpen(!isUserDropdownOpen);
    setOpenDropdown(null);
  };

  const userDisplayName = currentUser?.user_metadata?.name || currentUser?.user_metadata?.full_name || currentUser?.email?.split('@')[0] || 'User';
  const userFirstLetter = userDisplayName?.charAt(0).toUpperCase();
  const userEmail = currentUser?.email;

  const visibleNavItems = mainNavItems.filter(item => 
    !item.requiresAuth || (item.requiresAuth && currentUser)
  );

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      isScrolled || openDropdown || isUserDropdownOpen ? 'bg-slate-800 shadow-md' : 'bg-slate-900'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center space-x-2" onClick={() => {setOpenDropdown(null); setIsUserDropdownOpen(false);}}>
              {currentUser && currentUser.user_metadata?.avatar_url && (
                <img src={currentUser.user_metadata.avatar_url} alt="User Avatar" className="h-8 w-8 rounded-full" />
              )}
              {currentUser && !currentUser.user_metadata?.avatar_url && (
                <FaUserCircle className={`h-8 w-8 ${isScrolled || openDropdown || isUserDropdownOpen ? 'text-sky-400' : 'text-white'}`} />
              )}
              {!currentUser && (
                 <FaRobot className="text-2xl text-blue-600" />
              )}
              <span className={`text-xl font-bold ${isScrolled || openDropdown || isUserDropdownOpen ? 'text-sky-400' : 'text-white'}`}>Zeus AI</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center space-x-1">
            <Link
              href="/"
              onClick={() => {setOpenDropdown(null); setIsUserDropdownOpen(false);}}
              className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                pathname === '/' ? 'text-sky-400 bg-slate-700' : 
                (isScrolled || openDropdown || isUserDropdownOpen ? 'text-slate-200 hover:text-sky-300 hover:bg-slate-700' : 'text-slate-300 hover:text-sky-400 hover:bg-slate-800/60')
              }`}
            >
              <FaHome className="mr-1" /> Home
            </Link>

            {visibleNavItems.map((item) => (
              <div key={item.name} className="relative">
                <button
                  onClick={() => toggleMainDropdown(item.name)}
                  className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                    openDropdown === item.name ? 'text-sky-400 bg-slate-700' : 
                    (isScrolled || openDropdown || isUserDropdownOpen ? 'text-slate-200 hover:text-sky-300 hover:bg-slate-700' : 'text-slate-300 hover:text-sky-400 hover:bg-slate-800/60')
                  }`}
                >
                  <item.icon className="mr-1" /> {item.name}
                  {item.subItems && (openDropdown === item.name ? <FaChevronUp className="ml-1 h-3 w-3" /> : <FaChevronDown className="ml-1 h-3 w-3" />)}
                </button>
                {item.subItems && openDropdown === item.name && (
                  <div 
                    className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-md shadow-lg py-1 z-50 ring-1 ring-black ring-opacity-20"
                    onMouseLeave={() => setOpenDropdown(null)}
                  >
                    {item.subItems.map((subItem) => (
                      <Link
                        key={subItem.name}
                        href={subItem.href}
                        onClick={() => setOpenDropdown(null)}
                        className="block w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-sky-400"
                      >
                        {subItem.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {currentUser && (
              <Link
                href="/dashboard"
                onClick={() => {setOpenDropdown(null); setIsUserDropdownOpen(false);}}
                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                  pathname === '/dashboard' ? 'text-sky-400 bg-slate-700' : 
                  (isScrolled || openDropdown || isUserDropdownOpen ? 'text-slate-200 hover:text-sky-300 hover:bg-slate-700' : 'text-slate-300 hover:text-sky-400 hover:bg-slate-800/60')
                }`}
              >
                <FaUser className="mr-1" /> Dashboard
              </Link>
            )}

            {currentUser ? (
              <div className="relative ml-3" ref={userDropdownRef}> 
                <div>
                  <button
                    onClick={toggleUserDropdown}
                    className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 focus:ring-sky-500"
                    id="user-menu-button"
                    aria-expanded={isUserDropdownOpen}
                    aria-haspopup="true"
                  >
                    <span className="sr-only">Open user menu</span>
                    <div className="h-8 w-8 rounded-full bg-sky-500 flex items-center justify-center text-white font-semibold">
                      {userFirstLetter}
                    </div>
                    {userEmail && <span className={`ml-2 text-sm ${isScrolled || openDropdown || isUserDropdownOpen ? 'text-slate-200' : 'text-slate-300'}`}>{userEmail}</span>}
                  </button>
                </div>
                {isUserDropdownOpen && (
                  <div
                    className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-slate-800 ring-1 ring-black ring-opacity-20 focus:outline-none z-50"
                    role="menu"
                    aria-orientation="vertical"
                    aria-labelledby="user-menu-button"
                    tabIndex={-1}
                  >
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-sky-400"
                      role="menuitem"
                      tabIndex={-1}
                      id="user-menu-item-logout"
                    >
                      <FaSignOutAlt className="inline-block mr-2" /> Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                href="/login"
                onClick={() => {setOpenDropdown(null); setIsUserDropdownOpen(false);}}
                className={`ml-3 px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                  isScrolled || openDropdown || isUserDropdownOpen ? 'text-slate-100 bg-sky-600 hover:bg-sky-700' : 'text-slate-900 bg-sky-400 hover:bg-sky-500'
                }`}
              >
                <FaSignInAlt className="mr-1" /> Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 