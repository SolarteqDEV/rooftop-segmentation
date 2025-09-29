#!/usr/bin/env python3
"""
Rooftop Segmentation Project Visualization
이 스크립트는 지붕 분할 프로젝트의 결과를 시각화합니다.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
import random

def load_mask_data(mask_file_path):
    """마스크 JSON 파일을 로드합니다."""
    with open(mask_file_path, 'r') as f:
        mask_data = json.load(f)
    return mask_data

def create_mask_from_polygons(mask_data, image_size=(1024, 1024)):
    """폴리곤 데이터로부터 마스크 이미지를 생성합니다."""
    # 빈 이미지 생성
    mask_image = Image.new('RGB', image_size, (0, 0, 0))
    draw = ImageDraw.Draw(mask_image)
    
    # 각 shape에 대해 폴리곤 그리기
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    for i, shape in enumerate(mask_data.get('shapes', [])):
        if shape['shape_type'] == 'polygon':
            # 폴리곤 좌표 추출
            points = [(int(x), int(y)) for x, y in shape['points']]
            
            # 랜덤 색상 선택
            color = colors[i % len(colors)]
            
            # 폴리곤 그리기
            if len(points) >= 3:  # 최소 3개 점이 필요
                draw.polygon(points, fill=color, outline=(255, 255, 255))
    
    return mask_image

def visualize_sample_masks(data_dir, num_samples=6):
    """샘플 마스크들을 시각화합니다."""
    masks_path = Path(data_dir) / 'masks' / 's1024_z19' / 'train'
    mask_files = list(masks_path.glob('*.json'))
    
    if not mask_files:
        print("마스크 파일을 찾을 수 없습니다!")
        return
    
    # 랜덤하게 샘플 선택
    sample_files = random.sample(mask_files, min(num_samples, len(mask_files)))
    
    # 서브플롯 생성
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Rooftop Segmentation - Building Footprint Masks', fontsize=16)
    
    for i, mask_file in enumerate(sample_files):
        row = i // 3
        col = i % 3
        
        try:
            # 마스크 데이터 로드
            mask_data = load_mask_data(mask_file)
            
            # 마스크 이미지 생성
            mask_image = create_mask_from_polygons(mask_data)
            
            # 이미지 표시
            axes[row, col].imshow(mask_image)
            axes[row, col].set_title(f'Tile: {mask_file.stem.replace("_mask", "")}', fontsize=10)
            axes[row, col].axis('off')
            
            # 건물 개수 표시
            num_buildings = len(mask_data.get('shapes', []))
            axes[row, col].text(10, 30, f'Buildings: {num_buildings}', 
                              bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                              fontsize=8)
            
        except Exception as e:
            axes[row, col].text(0.5, 0.5, f'Error loading\n{mask_file.name}', 
                              ha='center', va='center', transform=axes[row, col].transAxes)
            axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return len(mask_files)

def analyze_dataset_stats(data_dir):
    """데이터셋 통계를 분석합니다."""
    masks_path = Path(data_dir) / 'masks' / 's1024_z19' / 'train'
    mask_files = list(masks_path.glob('*.json'))
    
    total_buildings = 0
    buildings_per_tile = []
    
    print("=== 데이터셋 분석 ===")
    print(f"총 타일 수: {len(mask_files)}")
    
    for mask_file in mask_files:
        try:
            mask_data = load_mask_data(mask_file)
            num_buildings = len(mask_data.get('shapes', []))
            total_buildings += num_buildings
            buildings_per_tile.append(num_buildings)
        except Exception as e:
            print(f"Error processing {mask_file}: {e}")
    
    if buildings_per_tile:
        print(f"총 건물 수: {total_buildings}")
        print(f"타일당 평균 건물 수: {np.mean(buildings_per_tile):.2f}")
        print(f"타일당 최대 건물 수: {max(buildings_per_tile)}")
        print(f"타일당 최소 건물 수: {min(buildings_per_tile)}")
    
    return {
        'total_tiles': len(mask_files),
        'total_buildings': total_buildings,
        'avg_buildings_per_tile': np.mean(buildings_per_tile) if buildings_per_tile else 0,
        'max_buildings_per_tile': max(buildings_per_tile) if buildings_per_tile else 0,
        'min_buildings_per_tile': min(buildings_per_tile) if buildings_per_tile else 0
    }

def main():
    """메인 함수"""
    print(" Rooftop Segmentation Project - 결과 시각화")
    print("=" * 50)
    
    data_dir = './data'
    
    # 데이터셋 통계 분석
    stats = analyze_dataset_stats(data_dir)
    
    # 샘플 마스크 시각화
    total_files = visualize_sample_masks(data_dir)
    
    print(f"\n 시각화 완료 {total_files}개의 마스크 파일이 있습니다.")

if __name__ == "__main__":
    main()
