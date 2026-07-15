import 'package:flutter/material.dart';
import '../../dashboard/presentation/dashboard_page.dart';
import '../../workout/presentation/workout_page.dart';
import '../../progress/presentation/progress_page.dart';
import '../../recovery/presentation/recovery_page.dart';
import '../../predictions/presentation/predictions_page.dart';
import '../../records/presentation/records_page.dart';
import '../../settings/presentation/settings_page.dart';

enum SidebarItem {
  dashboard,
  workout,
  progress,
  recovery,
  predictions,
  records,
  settings,
}

class ShellLayout extends StatefulWidget {
  const ShellLayout({super.key});

  @override
  State<ShellLayout> createState() => _ShellLayoutState();
}

class _ShellLayoutState extends State<ShellLayout> {
  bool _isExpanded = true;
  SidebarItem _selectedItem = SidebarItem.workout; // Start with Workout as specified

  final Map<SidebarItem, Widget> _pages = {
    SidebarItem.dashboard: const DashboardPage(),
    SidebarItem.workout: const WorkoutPage(),
    SidebarItem.progress: const ProgressPage(),
    SidebarItem.recovery: const RecoveryPage(),
    SidebarItem.predictions: const PredictionsPage(),
    SidebarItem.records: const RecordsPage(),
    SidebarItem.settings: const SettingsPage(),
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF070814),
      body: Row(
        children: [
          // Sidebar
          AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeInOut,
            width: _isExpanded ? 240 : 72, // 72 matches typical collapsed width nicely
            decoration: const BoxDecoration(
              color: Color(0xFF0A0B1E),
              border: Border(
                right: BorderSide(
                  color: Color(0xFF1F2035),
                  width: 1,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header (Logo + Collapse/Expand Toggle)
                _buildHeader(),
                const SizedBox(height: 16),
                // Sidebar Navigation List
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    children: [
                      _buildCategoryHeader('TRAINING'),
                      _buildNavigationItem(
                        item: SidebarItem.dashboard,
                        icon: Icons.dashboard_outlined,
                        label: 'Dashboard',
                      ),
                      _buildNavigationItem(
                        item: SidebarItem.workout,
                        icon: Icons.fitness_center_outlined,
                        label: 'Workout',
                      ),
                      _buildNavigationItem(
                        item: SidebarItem.progress,
                        icon: Icons.trending_up_outlined,
                        label: 'Progress',
                      ),
                      const SizedBox(height: 16),
                      _buildCategoryHeader('DATA'),
                      _buildNavigationItem(
                        item: SidebarItem.recovery,
                        icon: Icons.healing_outlined,
                        label: 'Recovery',
                      ),
                      _buildNavigationItem(
                        item: SidebarItem.predictions,
                        icon: Icons.psychology_outlined,
                        label: 'Predictions',
                      ),
                      _buildNavigationItem(
                        item: SidebarItem.records,
                        icon: Icons.emoji_events_outlined,
                        label: 'Records',
                      ),
                      const SizedBox(height: 16),
                      _buildCategoryHeader('SYSTEM'),
                      _buildNavigationItem(
                        item: SidebarItem.settings,
                        icon: Icons.settings_outlined,
                        label: 'Settings',
                      ),
                    ],
                  ),
                ),
                // User Profile Card at bottom
                _buildProfileCard(),
              ],
            ),
          ),
          // Content Area
          Expanded(
            child: Container(
              color: const Color(0xFF070814),
              child: _pages[_selectedItem] ?? const SizedBox.shrink(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.only(left: 16, right: 8, top: 16, bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          if (_isExpanded)
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: const Color(0xFF6366F1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.bolt,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                const Text(
                  'GymOS',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
              ],
            )
          else
            const SizedBox.shrink(),
          IconButton(
            onPressed: () {
              setState(() {
                _isExpanded = !_isExpanded;
              });
            },
            icon: Icon(
              _isExpanded ? Icons.chevron_left : Icons.chevron_right,
              color: Colors.grey[400],
            ),
            splashRadius: 20,
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryHeader(String title) {
    if (!_isExpanded) {
      return const Divider(color: Color(0xFF1F2035), height: 16);
    }
    return Padding(
      padding: const EdgeInsets.only(left: 12, top: 12, bottom: 6),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: Colors.grey[600],
          letterSpacing: 1.2,
        ),
      ),
    );
  }

  Widget _buildNavigationItem({
    required SidebarItem item,
    required IconData icon,
    required String label,
  }) {
    final isSelected = _selectedItem == item;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: InkWell(
        onTap: () {
          setState(() {
            _selectedItem = item;
          });
        },
        borderRadius: BorderRadius.circular(10),
        child: Container(
          height: 48,
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF6366F1).withOpacity(0.12) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: isSelected
                ? Border.all(color: const Color(0xFF6366F1).withOpacity(0.3), width: 1)
                : null,
          ),
          child: Row(
            mainAxisAlignment: _isExpanded ? MainAxisAlignment.start : MainAxisAlignment.center,
            children: [
              const SizedBox(width: 8),
              Icon(
                icon,
                color: isSelected ? const Color(0xFF6366F1) : Colors.grey[400],
                size: 22,
              ),
              if (_isExpanded) ...[
                const SizedBox(width: 14),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    color: isSelected ? Colors.white : Colors.grey[300],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(
            color: Color(0xFF1F2035),
            width: 1,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              // Avatar
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(19),
                ),
                child: const Center(
                  child: Text(
                    'N',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                ),
              ),
              if (_isExpanded) ...[
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Nguyễn Thiện Nhân',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        'Level 28 • Elite',
                        style: TextStyle(
                          fontSize: 11,
                          color: Color(0xFF8B5CF6),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
          if (_isExpanded) ...[
            const SizedBox(height: 12),
            // XP Progress Bar
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'XP Progress',
                  style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                ),
                Text(
                  '8,450 / 10,000 XP',
                  style: TextStyle(fontSize: 10, color: Colors.grey[400], fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 6),
            ClipRRect(
              borderRadius: BorderRadius.circular(3),
              child: const LinearProgressIndicator(
                value: 8450 / 10000,
                backgroundColor: Color(0xFF1F2035),
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF6366F1)),
                minHeight: 6,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
