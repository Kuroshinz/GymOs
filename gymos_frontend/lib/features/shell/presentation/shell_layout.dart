import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/extensions/context_extensions.dart';
import '../../../core/theme/theme_tokens.dart';

enum SidebarItem {
  dashboard('Dashboard', Icons.dashboard_outlined),
  workout('Workout', Icons.fitness_center_outlined),
  nutrition('Nutrition', Icons.restaurant_outlined),
  progress('Progress', Icons.trending_up_outlined),
  recovery('Recovery', Icons.healing_outlined),
  coach('AI Coach', Icons.psychology_outlined),
  calendar('Calendar', Icons.calendar_today_outlined),
  settings('Settings', Icons.settings_outlined),
  profile('Profile', Icons.person_outline);

  final String label;
  final IconData icon;

  const SidebarItem(this.label, this.icon);

  static SidebarItem fromIndex(int index) {
    return SidebarItem.values.firstWhere((item) => item.index == index, orElse: () => SidebarItem.workout);
  }
}

class ShellLayout extends StatefulWidget {
  final StatefulNavigationShell navigationShell;

  const ShellLayout({
    super.key,
    required this.navigationShell,
  });

  @override
  State<ShellLayout> createState() => _ShellLayoutState();
}

class _ShellLayoutState extends State<ShellLayout> {
  bool _isExpanded = true;

  void _onTap(int index) {
    widget.navigationShell.goBranch(
      index,
      initialLocation: index == widget.navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    final selectedItem = SidebarItem.fromIndex(widget.navigationShell.currentIndex);

    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      bottomNavigationBar: context.isMobile
          ? BottomNavigationBar(
              currentIndex: widget.navigationShell.currentIndex,
              onTap: _onTap,
              items: SidebarItem.values.take(5).map((item) {
                return BottomNavigationBarItem(
                  icon: Icon(item.icon),
                  label: item.label,
                );
              }).toList(),
            )
          : null,
      body: Row(
        children: [
          if (!context.isMobile) ...[
            // Sidebar Navigation for Desktop/Tablet
            AnimatedContainer(
              duration: GymOSTokens.durationDefault,
              curve: Curves.easeInOut,
              width: _isExpanded ? 240 : 76,
              decoration: BoxDecoration(
                color: const Color(0xFF0A0B1E),
                border: Border(
                  right: BorderSide(
                    color: context.theme.dividerColor,
                    width: 1,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(),
                  const SizedBox(height: GymOSTokens.space16),
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.symmetric(horizontal: GymOSTokens.space8),
                      children: [
                        _buildCategoryHeader('TRAINING'),
                        ..._buildNavGroup([
                          SidebarItem.dashboard,
                          SidebarItem.workout,
                          SidebarItem.progress,
                        ], selectedItem),
                        const SizedBox(height: GymOSTokens.space16),
                        _buildCategoryHeader('ANALYTICS'),
                        ..._buildNavGroup([
                          SidebarItem.recovery,
                          SidebarItem.coach,
                          SidebarItem.nutrition,
                          SidebarItem.calendar,
                        ], selectedItem),
                        const SizedBox(height: GymOSTokens.space16),
                        _buildCategoryHeader('SYSTEM'),
                        ..._buildNavGroup([
                          SidebarItem.profile,
                          SidebarItem.settings,
                        ], selectedItem),
                      ],
                    ),
                  ),
                  _buildProfileCard(),
                ],
              ),
            ),
          ],
          // Content Area
          Expanded(
            child: widget.navigationShell,
          ),
        ],
      ),
    );
  }

  List<Widget> _buildNavGroup(List<SidebarItem> items, SidebarItem selectedItem) {
    return items.map((item) {
      final isSelected = selectedItem == item;
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 2.0),
        child: InkWell(
          onTap: () => _onTap(item.index),
          borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
          child: Container(
            height: 48,
            decoration: BoxDecoration(
              color: isSelected ? const Color(0xFF6366F1).withOpacity(0.12) : Colors.transparent,
              borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
              border: isSelected
                  ? Border.all(color: const Color(0xFF6366F1).withOpacity(0.3), width: 1)
                  : null,
            ),
            child: Row(
              mainAxisAlignment: _isExpanded ? MainAxisAlignment.start : MainAxisAlignment.center,
              children: [
                const SizedBox(width: 12),
                Icon(
                  item.icon,
                  color: isSelected ? const Color(0xFF6366F1) : const Color(0xFF9E9EAF),
                  size: 20,
                ),
                if (_isExpanded) ...[
                  const SizedBox(width: 14),
                  Text(
                    item.label,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                      color: isSelected ? Colors.white : const Color(0xFF9E9EAF),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      );
    }).toList();
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
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: Colors.grey[600],
          letterSpacing: 1.2,
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
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  gradient: GymOSTokens.primaryGradient,
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
        ],
      ),
    );
  }
}
