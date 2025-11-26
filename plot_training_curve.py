import pandas as pd
import matplotlib.pyplot as plt

# 读取日志文件
log_path = "logs/your_exp_name/training_log.csv"  # 替换为实际路径
data = pd.read_csv(log_path)

# 绘制loss曲线
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(data['iteration'], data['loss'], label='Loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')
plt.title('Training Loss')

# 绘制PSNR曲线
plt.subplot(1, 2, 2)
plt.plot(data['iteration'], data['psnr'], color='orange', label='PSNR')
plt.xlabel('Iteration')
plt.ylabel('PSNR')
plt.title('Training PSNR')

plt.tight_layout()
plt.savefig('training_curve.png')
plt.show()