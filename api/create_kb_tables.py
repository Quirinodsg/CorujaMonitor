"""
Create Knowledge Base tables
"""
from database import engine
from models import Base, KnowledgeBaseEntry, AutoResolutionConfig, ResolutionAttempt, LearningSession

print("🔄 Creating Knowledge Base tables...")

try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Knowledge Base tables created successfully!")
    print("\n📚 Tables created:")
    print("   - knowledge_base")
    print("   - auto_resolution_config")
    print("   - resolution_attempts")
    print("   - learning_sessions")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
