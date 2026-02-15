import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HomeIcon,
  PlusCircleIcon,
  DocumentTextIcon,
  LinkIcon,
  SparklesIcon,
  PhotoIcon,
  VideoCameraIcon,
  SpeakerWaveIcon,
  ChatBubbleBottomCenterTextIcon,
  UserIcon,
  Cog6ToothIcon,
  XMarkIcon,
  ChartBarIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import { useAuthStore } from '../../store';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isImpersonating?: boolean;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const mainNavItems: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Create Post', href: '/posts/create', icon: PlusCircleIcon },
  { name: 'My Posts', href: '/posts', icon: DocumentTextIcon },
  { name: 'Connect Account', href: '/platforms', icon: LinkIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
];

const aiNavItems: NavItem[] = [
  { name: 'AI Caption', href: '/ai-caption', icon: SparklesIcon, badge: 'New' },
  { name: 'AI Image', href: '/ai-image', icon: PhotoIcon },
  { name: 'AI Video', href: '/ai-video', icon: VideoCameraIcon },
  { name: 'AI Voice', href: '/ai-voice', icon: SpeakerWaveIcon },
  { name: 'Messenger Bot', href: '/messenger', icon: ChatBubbleBottomCenterTextIcon },
];

const settingsNavItems: NavItem[] = [
  { name: 'Profile', href: '/profile', icon: UserIcon },
  { name: 'Business Profile', href: '/business-profile', icon: BuildingOfficeIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

// Custom Gem icon component
function GemIconCustom({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M6 3h12l4 6-10 12L2 9l4-6z" />
      <path d="M2 9h20" />
      <path d="M12 21L8 9l4-6 4 6-4 12z" />
    </svg>
  );
}

export function Sidebar({ isOpen, onClose, isImpersonating }: SidebarProps) {
  const { user } = useAuthStore();

  const NavSection = ({ items, title }: { items: NavItem[]; title?: string }) => (
    <div className="mb-6">
      {title && (
        <h3 className="px-4 mb-2 text-xs font-semibold text-text-muted uppercase tracking-wider">
          {title}
        </h3>
      )}
      <nav className="space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            onClick={onClose}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="flex-1">{item.name}</span>
            {item.badge && (
              <span className="badge badge-primary text-[10px]">{item.badge}</span>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Mobile close button */}
      <div className="lg:hidden flex items-center justify-between p-4 border-b border-white/5">
        <span className="text-lg font-bold gradient-text">Menu</span>
        <button onClick={onClose} className="btn-icon">
          <XMarkIcon className="w-6 h-6" />
        </button>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-6 px-3">
        <NavSection items={mainNavItems} />
        <NavSection items={aiNavItems} title="AI Tools" />
        <NavSection items={settingsNavItems} title="Settings" />
      </div>

      {/* Upgrade card */}
      {user?.profile?.subscription_plan === 'free' && (
        <div className="p-4">
          <div className="card gradient-border p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="icon-wrapper-sm bg-gradient-accent">
                <GemIconCustom className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Upgrade to Pro</h4>
                <p className="text-xs text-text-secondary">Unlock all features</p>
              </div>
            </div>
            <button className="btn-primary w-full py-2 text-sm">
              Upgrade Now
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="lg:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
          />
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <aside className={`hidden lg:flex lg:flex-col fixed left-0 ${isImpersonating ? 'top-[110px]' : 'top-[70px]'} bottom-[60px] w-[280px] bg-dark-800/95 backdrop-blur-xl border-r border-white/5 z-30`}>
        {sidebarContent}
      </aside>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="lg:hidden fixed left-0 top-0 bottom-0 w-[280px] bg-dark-800 z-50"
          >
            {sidebarContent}
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}

export default Sidebar;
