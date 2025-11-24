import os
from PIL import Image

def convert_jpeg_to_jpg(source_dir, target_dir):
    """
    将源文件夹中的所有JPEG文件转换为JPG格式并保存到目标文件夹
    
    参数:
        source_dir (str): 源文件夹路径
        target_dir (str): 目标文件夹路径
    """
    # 确保目标文件夹存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_dir):
        # 检查文件扩展名是否为jpeg（不区分大小写）
        if filename.lower().endswith(('.jpeg')):
            # 构造完整文件路径
            source_path = os.path.join(source_dir, filename)
            
            # 生成新文件名（替换扩展名为jpg）
            base_name = os.path.splitext(filename)[0]
            target_filename = base_name + '.jpg'
            target_path = os.path.join(target_dir, target_filename)
            
            try:
                # 打开图像文件并转换为JPG格式
                with Image.open(source_path) as img:
                    # 转换为RGB模式（避免部分JPEG保存为RGBA导致问题）
                    if img.mode in ('RGBA', 'LA'):
                        img = img.convert('RGB')
                    
                    # 保存为JPG格式
                    img.save(target_path, 'JPEG')
                    print(f"转换成功: {filename} -> {target_filename}")
                    
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")

if __name__ == "__main__":
    # 使用示例
    source_directory = "suannai\images"  # 替换为你的源文件夹路径
    target_directory = "suannai1\images"  # 替换为你的目标文件夹路径
    
    convert_jpeg_to_jpg(source_directory, target_directory)