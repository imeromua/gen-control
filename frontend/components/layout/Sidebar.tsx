'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Clock, Fuel, Settings, Calendar, FileText, Zap, BarChart2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/useAuth';

const navItems = [
  { href: '/',           label: 'Дашборд',       icon: LayoutDashboard },
  { href: '/shifts',     label: 'Зміни',         icon: Clock },
  { href: '/fuel',       label: 'Паливо',         icon: Fuel },
  { href: '/generators', label: 'Генератори',    icon: Settings, adminOnly: true },
  { href: '/outage',     label: 'Відключення',    icon: Calendar },
  { href: '/events',     label: 'Журнал подій',  icon: FileText },
  { href: '/reports',    label: 'Звіти',          icon: BarChart2 },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const isAdmin = (user as { role?: { name?: string } } | null)?.role?.name === 'ADMIN';

  return (
    <aside className="hidden lg:flex flex-col w-64 border-r bg-background h-full">
      <div className="flex items-center gap-2 px-6 py-4 border-b">
        <Zap className="h-6 w-6 text-yellow-500" />
        <span className="font-bold text-xl">GenControl</span>
      </div>
      <nav className="flex-1 py-4 space-y-1 px-3">
        {navItems.map((item) => {
          if (item.adminOnly && !isAdmin) return null;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                pathname === item.href
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
