"""
Download and setup AIDE model weights.

Since AIDE model weights are not publicly available, we'll:
1. Use pretrained ResNet-50 as the backbone (from torchvision)
2. Initialize the classifier head randomly
3. Provide instructions for users to add their own fine-tuned weights

For production use, you should fine-tune on your own dataset.
"""

import os
import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path


def create_aide_model():
    """Create AIDE model structure matching app/aide_model.py"""
    
    class AIDeDetector(nn.Module):
        def __init__(self, pretrained: bool = True):
            super(AIDeDetector, self).__init__()
            
            # Load pre-trained ResNet-50
            resnet = models.resnet50(pretrained=pretrained)
            
            # Remove the final FC layer
            self.features = nn.Sequential(*list(resnet.children())[:-1])
            
            # Binary classifier (Real vs AI-generated)
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Dropout(0.5),
                nn.Linear(2048, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 2)  # 2 classes: [real, fake]
            )
        
        def forward(self, x):
            features = self.features(x)
            output = self.classifier(features)
            return output
    
    return AIDeDetector(pretrained=True)


def save_model_checkpoint(model, save_path):
    """Save model checkpoint"""
    # Save full model state
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'model_type': 'AIDE',
        'architecture': 'ResNet-50 + Binary Classifier',
        'num_classes': 2,
        'input_size': 224,
        'note': 'This is a pretrained ResNet-50 backbone with randomly initialized classifier. For best results, fine-tune on your own dataset.'
    }
    
    torch.save(checkpoint, save_path)
    print(f"✅ Model checkpoint saved to: {save_path}")


def main():
    print("=" * 60)
    print("AIDE Model Setup")
    print("=" * 60)
    print()
    
    # Create models directory
    weights_dir = Path(__file__).parent / "models" / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    
    checkpoint_path = weights_dir / "aide_resnet50.pth"
    
    # Check if already exists
    if checkpoint_path.exists():
        print(f"⚠️  Model checkpoint already exists: {checkpoint_path}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    print("📥 Creating AIDE model...")
    print("   - Downloading ResNet-50 pretrained weights from ImageNet")
    print("   - Initializing binary classifier head")
    print()
    
    # Create model
    model = create_aide_model()
    
    print(f"✅ Model created successfully!")
    print(f"   - Backbone: ResNet-50 (ImageNet pretrained)")
    print(f"   - Classifier: 2048 → 512 → 2")
    print(f"   - Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print()
    
    # Save checkpoint
    print("💾 Saving model checkpoint...")
    save_model_checkpoint(model, checkpoint_path)
    
    # Verify
    file_size_mb = checkpoint_path.stat().st_size / (1024 * 1024)
    print(f"   - File size: {file_size_mb:.1f} MB")
    print()
    
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("📍 Model Location:")
    print(f"   {checkpoint_path}")
    print()
    print("🎯 Next Steps:")
    print()
    print("1. The model is now ready to use with pretrained ResNet-50 backbone")
    print()
    print("2. For production use, you should fine-tune on your dataset:")
    print("   - Prepare dataset: Real images vs AI-generated images")
    print("   - Run training script (see docs/TRAINING.md)")
    print("   - Replace this checkpoint with your fine-tuned weights")
    print()
    print("3. Test the model:")
    print("   python test_system.py")
    print()
    print("4. Start the service:")
    print("   ./start_gpu.sh")
    print()
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT NOTE:")
    print("   The classifier head is randomly initialized.")
    print("   For real detection tasks, fine-tuning is REQUIRED.")
    print("=" * 60)


if __name__ == "__main__":
    main()
