class PixelMap(object):
    def __init__(self, proto):
        self._proto = proto
        assert self.bits_per_pixel % 8 == 0, "Unsupported pixel density"
        assert self.width * self.height * self.bits_per_pixel / 8 == len(self._proto.data)

    @property
    def width(self):
        return self._proto.size.x

    @property
    def height(self):
        return self._proto.size.y

    @property
    def bits_per_pixel(self):
        return self._proto.bits_per_pixel

    @property
    def bytes_per_pixel(self):
        return self._proto.bits_per_pixel // 8

    def __getitem__(self, pos):
        x, y = pos

        assert 0 <= x < self.width
        assert 0 <= y < self.height

        index = self.width * y + x
        start = index * self.bytes_per_pixel
        data = self._proto.data[start : start + self.bytes_per_pixel]
        return data

    def is_set(self, p):
        return any(b != 0 for b in self[p])

    def is_empty(self, p):
        return not self.is_set(p)

    def print(self, wide=False):
        for y in range(self.height):
            for x in range(self.width):
                print("#" if self.is_set((x, y)) else " ", end=(" " if wide else ""))
            print("")

    def save_image(self, filename):
        data = [(0,0,self[x, y][0]) for y in range(self.height) for x in range(self.width)]
        from PIL import Image
        im= Image.new('RGB', (self.width, self.height))
        im.putdata(data)
        im.save(filename)
