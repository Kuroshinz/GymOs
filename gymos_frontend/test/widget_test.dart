import 'package:flutter_test/flutter_test.dart';
import 'package:gymos_frontend/main.dart';

void main() {
  testWidgets('App renders successfully smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const GymOSApp());
    expect(find.byType(GymOSApp), findsOneWidget);
  });
}
