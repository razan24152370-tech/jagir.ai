"""
Quick test to verify XAI implementation with upskilling dataset
Run this to check if everything is working correctly
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from jobs.ai_service import (
    _load_upskilling_data,
    _get_market_success_rate,
    _get_upskilling_recommendations,
    _get_market_insights,
)

def test_dataset_loading():
    """Test if dataset loads correctly"""
    print("=" * 60)
    print("TEST 1: Dataset Loading")
    print("=" * 60)
    
    df = _load_upskilling_data()
    if df is None:
        print("❌ FAILED: Dataset not found or failed to load")
        print("   Check: media/models/Employee_Upskilling_Dataset.csv exists")
        return False
    
    print(f"✅ SUCCESS: Loaded {len(df)} records")
    print(f"   Columns: {list(df.columns)}")
    return True

def test_market_success_rate():
    """Test market success rate calculation"""
    print("\n" + "=" * 60)
    print("TEST 2: Market Success Rate")
    print("=" * 60)
    
    # Test with common job titles
    test_titles = [
        "Software Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Product Manager",
    ]
    
    for title in test_titles:
        result = _get_market_success_rate(title)
        if result:
            print(f"✅ {title}:")
            print(f"   Success Rate: {result['success_rate']:.1f}%")
            print(f"   Sample Size: {result['sample_size']}")
        else:
            print(f"⚠️  {title}: No data found")
    
    return True

def test_upskilling_recommendations():
    """Test upskilling recommendations"""
    print("\n" + "=" * 60)
    print("TEST 3: Upskilling Recommendations")
    print("=" * 60)
    
    test_titles = [
        "Software Engineer",
        "Data Analyst",
    ]
    
    for title in test_titles:
        recs = _get_upskilling_recommendations(title)
        if recs:
            print(f"✅ {title}:")
            for rec in recs:
                print(f"   - {rec['skill']}: {rec['success_rate']:.1f}% success")
        else:
            print(f"⚠️  {title}: No recommendations found")
    
    return True

def test_full_insights():
    """Test full market insights"""
    print("\n" + "=" * 60)
    print("TEST 4: Full Market Insights")
    print("=" * 60)
    
    insights = _get_market_insights("Software Engineer")
    if insights:
        print("✅ Full insights generated:")
        if insights['market_success_rate']:
            print(f"   Market Success: {insights['market_success_rate']:.1f}% ({insights['sample_size']} profiles)")
        if insights['upskilling_recommendations']:
            print(f"   Upskilling Recs: {len(insights['upskilling_recommendations'])} available")
            for rec in insights['upskilling_recommendations'][:3]:
                print(f"      - {rec['skill']}")
    else:
        print("⚠️  No insights generated")
    
    return True

def main():
    print("\n🧪 XAI Implementation Test Suite\n")
    
    tests = [
        test_dataset_loading,
        test_market_success_rate,
        test_upskilling_recommendations,
        test_full_insights,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH ERROR:")
            print(f"   {type(e).__name__}: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - XAI system is ready!")
        print("\nNext steps:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Test recruiter ranking: /jobs/recruiter/applications/")
        print("3. Test job seeker recommendations: /jobs/browse/")
    else:
        print("\n⚠️  SOME TESTS FAILED - Check errors above")
        print("\nCommon issues:")
        print("- Dataset not found: Check media/models/Employee_Upskilling_Dataset.csv")
        print("- No matches: Job titles may not match dataset values")
        print("- Low sample size: Try different job titles")

if __name__ == "__main__":
    main()
