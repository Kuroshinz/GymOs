abstract class LocalStorageService {
  Future<void> init();
  
  Future<void> write<T>(String key, T value);
  
  Future<T?> read<T>(String key);
  
  Future<void> delete(String key);
  
  Future<void> clear();
  
  Future<bool> hasKey(String key);
}
